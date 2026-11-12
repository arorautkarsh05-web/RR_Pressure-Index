"""
RR PRESSURE INDEX 2027 — PHASE 02.1: PRESSURE ENGINE V2
Architecturally Decoupled Batting Pressure vs Bowling Execution Leverage.

Features:
- Batting Pressure (Psi_bat): Chase difficulty & crisis resource depletion.
- Bowling Execution Leverage (Lambda_bowl): Pre-delivery Win-Probability swing & match closeness.
- Out-of-Match CV calibrated Win-Probability model.
- Division-by-zero guarded continuous first-innings resource model.
- Explicit Super Over isolation.
"""

import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score, log_loss
from sklearn.model_selection import KFold

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
TABLES_DIR = os.path.join(BASE_DIR, "outputs", "tables")
os.makedirs(TABLES_DIR, exist_ok=True)

BOWLER_DISMISSALS = {"Caught", "Bowled", "LBW", "Stump", "Hit Wicket"}

def fit_empirical_resource_model(df_inn1):
    """
    Fits continuous empirical resource grid E[R | balls_left, wkts_left]
    from historical 1st innings data.
    """
    df = df_inn1.copy()
    df['over_bucket'] = np.clip(df['balls_remaining'] // 6, 0, 20)
    df['wkt_bucket'] = np.clip(df['wickets_remaining'], 1, 10)
    
    grid = df.groupby(['over_bucket', 'wkt_bucket'])['runs_remaining'].mean().to_dict()
    
    def get_expected_remaining(balls_left, wkts_left):
        ob = int(np.clip(balls_left // 6, 0, 20))
        wb = int(np.clip(wkts_left, 1, 10))
        val = grid.get((ob, wb))
        if pd.notna(val):
            return val
        return (balls_left / 6.0) * (5.0 + 3.5 * (wb / 10.0))
        
    return get_expected_remaining

def build_pressure_engine_v2():
    print("=" * 80)
    print("RR PRESSURE INDEX 2027 — PRESSURE ENGINE V2: STATISTICAL HARDENING")
    print("=" * 80)

    # 1. Load Raw Datasets
    print("\n[Step 1/6] Ingesting and filtering eligible matches...")
    comps = pd.read_csv(os.path.join(RAW_DIR, "competitions.csv"))
    matches = pd.read_csv(os.path.join(RAW_DIR, "matches.csv"))
    bbb = pd.read_csv(os.path.join(RAW_DIR, "ball_by_ball.csv"), low_memory=False)

    def is_eligible(row):
        cname = str(row['comp_name'])
        mformat = str(row['match_format'])
        return ('IPL' in cname or 'Indian Premier League' in cname) or (mformat == 'T20I')

    comps['is_eligible'] = comps.apply(is_eligible, axis=1)
    eligible_comp_ids = set(comps[comps['is_eligible']]['comp_id'])
    
    ipl_comp_ids = set(comps[comps['comp_name'].str.contains('IPL|Indian Premier League', case=False, na=False)]['comp_id'])
    comp_format_map = {cid: ('IPL' if cid in ipl_comp_ids else 'T20I') for cid in eligible_comp_ids}
    comp_season_map = comps.set_index('comp_id')['season'].to_dict()

    eligible_matches = matches[matches['comp_id'].isin(eligible_comp_ids)].copy()
    eligible_matches['format'] = eligible_matches['comp_id'].map(comp_format_map)
    eligible_matches['season'] = eligible_matches['comp_id'].map(comp_season_map)
    eligible_match_ids = set(eligible_matches['match_id'])

    bbb_el = bbb[bbb['match_id'].isin(eligible_match_ids)].copy()
    print(f"  Loaded {len(bbb_el):,} deliveries across {len(eligible_match_ids)} matches.")

    # Match-level metadata join
    match_meta = eligible_matches[['match_id', 'format', 'stage', 'knock_out', 'match_date', 'season',
                                   'first_inn_revised_overs', 'second_inn_revised_overs', 'revised_target',
                                   'win_team_id']].set_index('match_id')
    bbb_el = bbb_el.join(match_meta, on='match_id')

    # Derived delivery base attributes
    bbb_el['is_legal'] = ~bbb_el['extras_type'].isin(['wide', 'Overstep', 'other'])
    bbb_el['team_runs'] = bbb_el['runs'] + (bbb_el['extras_type'] == 'wide').astype(int) + \
                          (bbb_el['extras_type'].isin(['Overstep', 'other'])).astype(int) + bbb_el['extras_2_runs']

    bbb_el['bowler_runs_conceded'] = np.where(
        bbb_el['extras_type'].isin(['byes', 'legbyes']),
        0,
        bbb_el['runs'] + (bbb_el['extras_type'] == 'wide').astype(int) + \
        (bbb_el['extras_type'].isin(['Overstep', 'other'])).astype(int) + bbb_el['extras_2_runs']
    )
    bbb_el['is_bowler_wicket'] = bbb_el['is_wicket'] & bbb_el['dismissal_type'].isin(BOWLER_DISMISSALS)

    # Sort strictly chronologically
    bbb_el = bbb_el.sort_values(['match_id', 'innings', 'innings_ball_num']).reset_index(drop=True)

    print("\n[Step 2/6] Reconstructing Pre-Delivery Match State (Zero Outcome Leakage)...")
    bbb_el['cum_runs_before'] = bbb_el.groupby(['match_id', 'innings'])['team_runs'].cumsum() - bbb_el['team_runs']
    bbb_el['cum_wickets_before'] = bbb_el.groupby(['match_id', 'innings'])['is_wicket'].cumsum() - bbb_el['is_wicket'].astype(int)
    bbb_el['legal_balls_bowled'] = bbb_el.groupby(['match_id', 'innings'])['is_legal'].cumsum() - bbb_el['is_legal'].astype(int)

    # Innings overs allocation
    inn_overs = np.where(
        (bbb_el['innings'] == 2) & bbb_el['second_inn_revised_overs'].notna(),
        bbb_el['second_inn_revised_overs'],
        np.where(
            (bbb_el['innings'] == 1) & bbb_el['first_inn_revised_overs'].notna(),
            bbb_el['first_inn_revised_overs'],
            20.0
        )
    )
    bbb_el['total_inn_balls'] = (inn_overs * 6).astype(int)
    bbb_el['balls_remaining'] = np.maximum(0, bbb_el['total_inn_balls'] - bbb_el['legal_balls_bowled'])
    bbb_el['wickets_remaining'] = np.maximum(0, 10 - bbb_el['cum_wickets_before'])
    
    # Division-by-zero safe overs elapsed (minimum 1/6 over)
    bbb_el['overs_elapsed'] = np.maximum(1.0 / 6.0, bbb_el['legal_balls_bowled'] / 6.0)

    # Flag Super Overs
    bbb_el['is_super_over'] = bbb_el['innings'].isin([3, 4])

    # Final innings 1 totals for target derivation
    inn1_totals = bbb_el[bbb_el['innings'] == 1].groupby('match_id')['team_runs'].sum().to_dict()
    bbb_el['inn1_final_score'] = bbb_el['match_id'].map(inn1_totals)

    # Target
    bbb_el['target'] = np.where(
        bbb_el['revised_target'].notna() & (bbb_el['innings'] == 2),
        bbb_el['revised_target'],
        bbb_el['inn1_final_score'] + 1
    )
    bbb_el['runs_required'] = np.where(
        bbb_el['innings'] == 2,
        np.maximum(0, bbb_el['target'] - bbb_el['cum_runs_before']),
        np.nan
    )
    bbb_el['rrr'] = np.where(
        (bbb_el['innings'] == 2) & (bbb_el['balls_remaining'] > 0),
        (bbb_el['runs_required'] / bbb_el['balls_remaining']) * 6.0,
        np.nan
    )

    # -------------------------------------------------------------
    # 3. FIRST-INNINGS MODEL CALIBRATION (CRITICAL CORRECTION B)
    # -------------------------------------------------------------
    print("\n[Step 3/6] Calibrating First-Innings Expected Score & Crisis Model...")
    bbb_inn1 = bbb_el[bbb_el['innings'] == 1].copy()
    bbb_inn1['runs_remaining'] = bbb_inn1['inn1_final_score'] - bbb_inn1['cum_runs_before']
    get_exp_rem = fit_empirical_resource_model(bbb_inn1)

    exp_rem = [get_exp_rem(b, w) for b, w in zip(bbb_el['balls_remaining'], bbb_el['wickets_remaining'])]
    bbb_el['expected_runs_remaining'] = np.where(bbb_el['innings'] == 1, exp_rem, np.nan)
    bbb_el['expected_total_score'] = np.where(bbb_el['innings'] == 1, bbb_el['cum_runs_before'] + bbb_el['expected_runs_remaining'], np.nan)

    # Continuous Resource Depletion vs Time Remaining
    res_fraction = np.clip(bbb_el['expected_runs_remaining'] / 170.8, 0.0, 1.0)
    time_fraction = np.clip(bbb_el['balls_remaining'] / 120.0, 0.0, 1.0)
    crisis_gap = np.maximum(0.0, time_fraction - res_fraction)
    bbb_el['collapse_strain'] = np.clip(crisis_gap / (time_fraction + 0.1), 0.0, 1.0)

    # Continuous Death Acceleration Strain based on balls remaining
    bbb_el['death_strain'] = np.where(
        bbb_el['balls_remaining'] <= 30,
        0.55 + 0.40 * (1.0 - (bbb_el['balls_remaining'] / 30.0)),
        np.where(bbb_el['balls_remaining'] <= 84, 0.25, 0.10)
    )

    # Format-aware Dynamic Par
    format_season_par = bbb_inn1.groupby(['format', 'season'])['inn1_final_score'].mean().to_dict()
    bbb_el['dynamic_par'] = [format_season_par.get((f, s), 170.0) for f, s in zip(bbb_el['format'], bbb_el['season'])]
    
    par_deficit = np.clip((bbb_el['dynamic_par'] - bbb_el['expected_total_score']) / 35.0, 0.0, 1.0)
    bbb_el['par_deficit_strain'] = par_deficit

    # Batting Pressure in Innings 1
    psi_bat_inn1 = np.clip(
        0.45 * bbb_el['collapse_strain'] + 0.35 * bbb_el['death_strain'] + 0.20 * bbb_el['par_deficit_strain'],
        0.0, 1.0
    )

    # -------------------------------------------------------------
    # 4. SECOND-INNINGS BATTING PRESSURE
    # -------------------------------------------------------------
    print("\n[Step 4/6] Formulating Second-Innings Batting Pressure...")
    rrr_clamped = bbb_el['rrr'].clip(lower=0, upper=30)
    rate_strain = 1.0 / (1.0 + np.exp(-0.55 * (rrr_clamped - 9.0)))
    wkt_scarcity = 1.0 - ((bbb_el['wickets_remaining'] - 1) / 9.0) ** 0.85
    urgency = 1.0 - np.sqrt(np.maximum(0, bbb_el['balls_remaining']) / 120.0)
    target_difficulty = np.clip((bbb_el['target'] - 130.0) / 60.0, 0.6, 1.3)

    psi_bat_inn2 = np.clip(
        (0.40 * rate_strain + 0.30 * wkt_scarcity + 0.30 * (rate_strain * urgency)) * target_difficulty,
        0.0, 1.0
    )

    is_playoff = (bbb_el['knock_out'] == 1) | bbb_el['stage'].isin(['Final', 'Qualifier', 'Eliminator', 'Semi Final'])
    playoff_mult = np.where(is_playoff, 1.10, 1.0)

    # Unified Batting Pressure (Psi_bat)
    bbb_el['psi_bat'] = np.select(
        [bbb_el['is_super_over'], bbb_el['innings'] == 2, bbb_el['innings'] == 1],
        [1.0, psi_bat_inn2 * playoff_mult, psi_bat_inn1 * playoff_mult],
        default=0.25
    )
    bbb_el['psi_bat'] = np.clip(bbb_el['psi_bat'], 0.0, 1.0)

    # -------------------------------------------------------------
    # 5. BOWLING EXECUTION LEVERAGE (CRITICAL CORRECTION A)
    # -------------------------------------------------------------
    print("\n[Step 5/6] Training Pre-Delivery Win-Probability Model for Bowling Leverage...")
    inn2_teams = bbb_el[bbb_el['innings'] == 2].groupby('match_id')['batting_team_id'].first().to_dict()
    bbb_el['chasing_team_id'] = bbb_el['match_id'].map(inn2_teams)
    bbb_el['chase_won'] = np.where(
        bbb_el['win_team_id'].notna() & (bbb_el['innings'] == 2),
        (bbb_el['chasing_team_id'] == bbb_el['win_team_id']).astype(float),
        np.nan
    )

    inn2_mask = (bbb_el['innings'] == 2) & bbb_el['chase_won'].notna()
    df_inn2 = bbb_el[inn2_mask].copy()

    df_inn2['rrr_clamped'] = df_inn2['rrr'].clip(lower=0, upper=36)
    df_inn2['req_per_ball'] = df_inn2['runs_required'] / (df_inn2['balls_remaining'] + 1)
    df_inn2['wkt_ratio'] = df_inn2['wickets_remaining'] / 10.0
    df_inn2['balls_ratio'] = df_inn2['balls_remaining'] / 120.0
    df_inn2['target_scaled'] = (df_inn2['target'] - 165.0) / 40.0

    wp_features = ['rrr_clamped', 'req_per_ball', 'wkt_ratio', 'balls_ratio', 'target_scaled']
    X_wp = df_inn2[wp_features].fillna(0)
    y_wp = df_inn2['chase_won']

    unique_matches = df_inn2['match_id'].unique()
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    oof_wp = np.zeros(len(df_inn2))

    for train_m_idx, val_m_idx in kf.split(unique_matches):
        train_m = unique_matches[train_m_idx]
        val_m = unique_matches[val_m_idx]
        
        train_sel = df_inn2['match_id'].isin(train_m)
        val_sel = df_inn2['match_id'].isin(val_m)
        
        lr = LogisticRegression(max_iter=1000, C=1.0)
        lr.fit(X_wp[train_sel], y_wp[train_sel])
        oof_wp[val_sel] = lr.predict_proba(X_wp[val_sel])[:, 1]

    df_inn2['wp_chase'] = oof_wp
    
    bbb_el['wp_chase'] = np.nan
    bbb_el.loc[inn2_mask, 'wp_chase'] = df_inn2['wp_chase']

    # Match Closeness / Swing: Closeness = 4 * WP * (1 - WP) in [0, 1]
    closeness_inn2 = 4.0 * bbb_el['wp_chase'] * (1.0 - bbb_el['wp_chase'])
    
    urgency_death = np.clip(1.0 - (bbb_el['balls_remaining'] / 30.0), 0.0, 1.0)
    lambda_bowl_inn2 = np.clip(
        closeness_inn2 * (0.65 + 0.35 * urgency_death),
        0.0, 1.0
    )

    par_surplus = np.clip((bbb_el['expected_total_score'] - bbb_el['dynamic_par']) / 30.0, 0.0, 1.0)
    lambda_bowl_inn1 = np.clip(
        0.45 * bbb_el['death_strain'] + 0.35 * par_surplus + 0.20 * (1.0 - bbb_el['collapse_strain']),
        0.0, 1.0
    )

    bbb_el['lambda_bowl'] = np.select(
        [bbb_el['is_super_over'], bbb_el['innings'] == 2, bbb_el['innings'] == 1],
        [1.0, lambda_bowl_inn2 * playoff_mult, lambda_bowl_inn1 * playoff_mult],
        default=0.25
    )
    bbb_el['lambda_bowl'] = np.clip(bbb_el['lambda_bowl'], 0.0, 1.0)

    # -------------------------------------------------------------
    # 6. OPERATIONAL DOMAINS & EXPORT
    # -------------------------------------------------------------
    print("\n[Step 6/6] Finalizing Operational Domains & Exporting Features...")
    bbb_el['is_bat_pressure'] = bbb_el['psi_bat'] >= 0.55
    bbb_el['is_bat_normal'] = bbb_el['psi_bat'] < 0.45
    
    bbb_el['is_bowl_leverage'] = bbb_el['lambda_bowl'] >= 0.50
    bbb_el['is_bowl_normal'] = bbb_el['lambda_bowl'] < 0.40

    bbb_el['is_bat_chasing_clutch'] = (bbb_el['innings'] == 2) & bbb_el['is_bat_pressure']
    bbb_el['is_bowl_chasing_clutch'] = (bbb_el['innings'] == 2) & bbb_el['is_bowl_leverage']

    bbb_el['is_collapse_crisis'] = (bbb_el['overid'] <= 12) & (bbb_el['wickets_remaining'] <= 7) & (bbb_el['collapse_strain'] >= 0.40)
    bbb_el['is_death_overs'] = (bbb_el['overid'] >= 16) & (bbb_el['innings'].isin([1, 2]))

    # Export feature store v2
    v2_path = os.path.join(TABLES_DIR, "delivery_pressure_features_v2.csv")
    bbb_el.to_csv(v2_path, index=False)
    size_mb = os.path.getsize(v2_path) / (1024 * 1024)
    print(f"  Saved hardened feature store to: {v2_path} ({size_mb:.2f} MB, {len(bbb_el):,} deliveries)")

    # Export Validation Tables
    bat_val = bbb_el.groupby('overid').agg(
        total_balls=('innings_ball_num', 'count'),
        mean_psi_bat=('psi_bat', 'mean'),
        std_psi_bat=('psi_bat', 'std'),
        prop_bat_pressure=('is_bat_pressure', 'mean')
    ).reset_index()
    bat_val_path = os.path.join(TABLES_DIR, "batting_pressure_validation.csv")
    bat_val.to_csv(bat_val_path, index=False)
    print(f"  Saved Batting Pressure Validation Table to: {bat_val_path}")

    bowl_val = bbb_el.groupby('overid').agg(
        total_balls=('innings_ball_num', 'count'),
        mean_lambda_bowl=('lambda_bowl', 'mean'),
        std_lambda_bowl=('lambda_bowl', 'std'),
        prop_bowl_leverage=('is_bowl_leverage', 'mean')
    ).reset_index()
    bowl_val_path = os.path.join(TABLES_DIR, "bowling_leverage_validation.csv")
    bowl_val.to_csv(bowl_val_path, index=False)
    print(f"  Saved Bowling Leverage Validation Table to: {bowl_val_path}")

    print("\nVALIDATION METRICS SUMMARY:")
    print(f"  Batting Pressure Deliveries (Psi >= 0.55): {bbb_el['is_bat_pressure'].sum():,} ({bbb_el['is_bat_pressure'].mean()*100:.1f}%)")
    print(f"  Bowling Leverage Deliveries (Lambda >= 0.50): {bbb_el['is_bowl_leverage'].sum():,} ({bbb_el['is_bowl_leverage'].mean()*100:.1f}%)")
    print(f"  Decoupled Deliveries (High Batting Pressure BUT Low Bowling Leverage): {((bbb_el['is_bat_pressure']) & (~bbb_el['is_bowl_leverage'])).sum():,} balls")
    print(f"  Win-Probability Brier Score: {brier_score_loss(y_wp, df_inn2['wp_chase']):.4f} | ROC AUC: {roc_auc_score(y_wp, df_inn2['wp_chase']):.4f}")
    print("=" * 80)

    return bbb_el

if __name__ == "__main__":
    build_pressure_engine_v2()
