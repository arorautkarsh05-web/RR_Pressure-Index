"""
RR PRESSURE INDEX 2027 — PHASE 03: BOWLER INTELLIGENCE ENGINE
Comprehensive Player-Level Analysis for All Eligible Bowlers.

Calculates:
- Pressure legal balls bowled, runs conceded, economy rate, bowler wickets
- Conceded boundary percentage, dot-ball percentage, bowler wicket rate
- Context-expected baseline (E[Econ], E[Bound%], E[Dot%], E[Wkt%])
- Context-adjusted delta (Delta_context = Y_pressure - E[Y])
- Normal baseline & raw delta (Delta_raw = Y_pressure - Y_normal)
- Phase confounding gap (Gap = Delta_raw - Delta_context)
- Match-level consistency (standard deviation, CV, and success rate)
- Bayesian posteriors & exact 95% Credible Intervals (Beta-Binomial & Clustered Normal-Normal)
- Specialized contextual metrics:
  * Chasing Defense (CCI): Innings 2 leverage balls bowled
  * Powerplay / Early Leverage (CPI): Overs 1-10 leverage balls bowled
  * Death Execution (DEI): Overs 16-20 leverage balls bowled
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES_DIR = os.path.join(BASE_DIR, "outputs", "tables")
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(TABLES_DIR, exist_ok=True)

def build_bowler_intelligence():
    print("=" * 80)
    print("RR PRESSURE INDEX 2027 — BOWLER INTELLIGENCE ENGINE")
    print("=" * 80)

    # 1. Load Data
    features_path = os.path.join(TABLES_DIR, "delivery_pressure_features_v2.csv")
    base_path = os.path.join(TABLES_DIR, "context_adjusted_baselines.csv")
    bayes_path = os.path.join(TABLES_DIR, "bayesian_model_comparison.csv")
    
    print(f"\n[Step 1/5] Loading feature store from: {features_path}")
    df_del = pd.read_csv(features_path, low_memory=False)
    df_base = pd.read_csv(base_path)
    df_bayes = pd.read_csv(bayes_path)

    # Filter legal deliveries bowled by bowler (is_legal == True)
    df_bowl_del = df_del[df_del['is_legal']].copy()
    print(f"  Total Bowling Legal Balls Bowled: {len(df_bowl_del):,}")

    # Vectorized flags
    df_bowl_del['lev_ball_flag'] = df_bowl_del['is_bowl_leverage'].astype(int)
    df_bowl_del['lev_runs_val'] = np.where(df_bowl_del['is_bowl_leverage'], df_bowl_del['bowler_runs_conceded'], 0)
    df_bowl_del['lev_wkts_val'] = np.where(df_bowl_del['is_bowl_leverage'] & df_bowl_del['is_bowler_wicket'], 1, 0)
    df_bowl_del['lev_dots_val'] = np.where(df_bowl_del['is_bowl_leverage'] & (df_bowl_del['bowler_runs_conceded'] == 0), 1, 0)
    df_bowl_del['lev_bnds_val'] = np.where(df_bowl_del['is_bowl_leverage'] & df_bowl_del['runs'].isin([4, 6]), 1, 0)

    # 2. Match-Level Aggregate for Consistency Analysis
    print("\n[Step 2/5] Computing Match-Level Bowling Performance & Consistency Metrics...")
    m_bowl = df_bowl_del.groupby(['match_id', 'bowler_id']).agg(
        match_balls=('innings_ball_num', 'count'),
        match_runs=('bowler_runs_conceded', 'sum'),
        match_wkts=('is_bowler_wicket', 'sum'),
        match_leverage_balls=('lev_ball_flag', 'sum'),
        match_leverage_runs=('lev_runs_val', 'sum'),
        match_leverage_wkts=('lev_wkts_val', 'sum')
    ).reset_index()

    m_bowl['match_lev_econ'] = np.where(
        m_bowl['match_leverage_balls'] > 0,
        (m_bowl['match_leverage_runs'] / m_bowl['match_leverage_balls']) * 6.0,
        np.nan
    )

    # Match-level consistency per bowler
    bowl_consistency = []
    for pid, grp in m_bowl.groupby('bowler_id'):
        p_grp = grp[grp['match_leverage_balls'] >= 6]  # Matches with at least 1 full over of leverage
        n_lev_matches = len(p_grp)
        if n_lev_matches >= 3:
            econ_std = float(p_grp['match_lev_econ'].std())
            econ_mean = float(p_grp['match_lev_econ'].mean())
            econ_cv = float(econ_std / econ_mean) if econ_mean > 0 else np.nan
            # Success rate: matches where leverage economy <= 8.50 rpo
            success_rate = float((p_grp['match_lev_econ'] <= 8.50).mean())
        else:
            econ_std = np.nan
            econ_cv = np.nan
            success_rate = np.nan
            
        bowl_consistency.append({
            'player_id': pid,
            'total_matches_played': grp['match_id'].nunique(),
            'leverage_matches_count': (grp['match_leverage_balls'] > 0).sum(),
            'qualified_leverage_matches': n_lev_matches,
            'match_econ_std': econ_std,
            'match_econ_cv': econ_cv,
            'match_success_rate_sub85': success_rate
        })
    df_consistency = pd.DataFrame(bowl_consistency)

    # 3. Contextual Subsets (Chasing Defense, Powerplay/Collapse, Death Execution)
    print("\n[Step 3/5] Computing Specialized Contextual Partitions (CCI, CPI, DEI)...")
    
    # Chasing Defense: Innings 2 bowling execution leverage
    cci_df = df_bowl_del[df_bowl_del['is_bowl_chasing_clutch']].groupby('bowler_id').agg(
        chase_lev_balls=('innings_ball_num', 'count'),
        chase_lev_runs=('bowler_runs_conceded', 'sum'),
        chase_lev_boundaries=('runs', lambda s: (s.isin([4, 6])).sum()),
        chase_lev_dots=('bowler_runs_conceded', lambda s: (s == 0).sum()),
        chase_lev_wkts=('is_bowler_wicket', 'sum')
    ).reset_index().rename(columns={'bowler_id': 'player_id'})
    cci_df['chase_lev_econ'] = (cci_df['chase_lev_runs'] / cci_df['chase_lev_balls']) * 6.0
    cci_df['chase_lev_sr'] = np.where(cci_df['chase_lev_wkts'] > 0, cci_df['chase_lev_balls'] / cci_df['chase_lev_wkts'], np.nan)

    # Powerplay / Early Pressure: overs 1-10 leverage balls bowled
    cpi_df = df_bowl_del[(df_bowl_del['overid'] <= 10) & df_bowl_del['is_bowl_leverage']].groupby('bowler_id').agg(
        powerplay_lev_balls=('innings_ball_num', 'count'),
        powerplay_lev_runs=('bowler_runs_conceded', 'sum'),
        powerplay_lev_boundaries=('runs', lambda s: (s.isin([4, 6])).sum()),
        powerplay_lev_dots=('bowler_runs_conceded', lambda s: (s == 0).sum()),
        powerplay_lev_wkts=('is_bowler_wicket', 'sum')
    ).reset_index().rename(columns={'bowler_id': 'player_id'})
    cpi_df['powerplay_lev_econ'] = (cpi_df['powerplay_lev_runs'] / cpi_df['powerplay_lev_balls']) * 6.0
    cpi_df['powerplay_lev_sr'] = np.where(cpi_df['powerplay_lev_wkts'] > 0, cpi_df['powerplay_lev_balls'] / cpi_df['powerplay_lev_wkts'], np.nan)

    # Death Execution: overs 16-20 bowling execution leverage
    dei_df = df_bowl_del[df_bowl_del['is_death_overs'] & df_bowl_del['is_bowl_leverage']].groupby('bowler_id').agg(
        death_lev_balls=('innings_ball_num', 'count'),
        death_lev_runs=('bowler_runs_conceded', 'sum'),
        death_lev_boundaries=('runs', lambda s: (s.isin([4, 6])).sum()),
        death_lev_dots=('bowler_runs_conceded', lambda s: (s == 0).sum()),
        death_lev_wkts=('is_bowler_wicket', 'sum')
    ).reset_index().rename(columns={'bowler_id': 'player_id'})
    dei_df['death_lev_econ'] = (dei_df['death_lev_runs'] / dei_df['death_lev_balls']) * 6.0
    dei_df['death_lev_sr'] = np.where(dei_df['death_lev_wkts'] > 0, dei_df['death_lev_balls'] / dei_df['death_lev_wkts'], np.nan)

    # 4. Integrate Baselines & Bayesian Posteriors
    print("\n[Step 4/5] Merging Context-Adjusted Baselines & Bayesian Posteriors...")
    bowl_bayes = df_bayes[df_bayes['role'] == 'bowler'].copy()
    bowl_base = df_base[df_base['role'] == 'bowler'].copy()

    # Leverage aggregate totals
    lev_totals = df_bowl_del[df_bowl_del['is_bowl_leverage']].groupby('bowler_id').agg(
        lev_runs_conceded=('bowler_runs_conceded', 'sum'),
        lev_wkts=('is_bowler_wicket', 'sum')
    ).reset_index().rename(columns={'bowler_id': 'player_id'})

    # Competitions played
    comp_played = df_bowl_del.groupby('bowler_id')['format'].unique().apply(lambda arr: "/".join(sorted(arr))).reset_index().rename(columns={'bowler_id': 'player_id', 'format': 'competitions'})

    # Merge sequentially on player_id
    merged = pd.merge(bowl_bayes, bowl_base[['player_id', 'death_leverage_share', 'pp_leverage_share', 'norm_econ', 'norm_boundary_pct', 'norm_dot_pct', 'norm_wicket_pct']], on='player_id', how='left')
    merged = pd.merge(merged, lev_totals, on='player_id', how='left')
    merged = pd.merge(merged, df_consistency, on='player_id', how='left')
    merged = pd.merge(merged, cci_df, on='player_id', how='left')
    merged = pd.merge(merged, cpi_df, on='player_id', how='left')
    merged = pd.merge(merged, dei_df, on='player_id', how='left')
    merged = pd.merge(merged, comp_played, on='player_id', how='left')

    # Derived Bowler Metrics
    merged['press_bowl_avg'] = np.where(merged['lev_wkts'] > 0, merged['lev_runs_conceded'] / merged['lev_wkts'], np.nan)
    merged['press_bowl_sr'] = np.where(merged['lev_wkts'] > 0, merged['pressure_balls'] / merged['lev_wkts'], np.nan)
    merged['sample_confidence'] = np.where(
        merged['pressure_balls'] >= 100, 'Tier A (High Confidence: N>=100)',
        np.where(merged['pressure_balls'] >= 60, 'Tier B (Moderate Confidence: 60<=N<100)', 'Tier C (Provisional: N<60)')
    )

    # 5. Export Bowler Profiles
    out_path = os.path.join(TABLES_DIR, "bowler_performance_profiles.csv")
    merged.to_csv(out_path, index=False)
    print(f"  Successfully exported {len(merged)} bowler performance profiles to: {out_path}")
    print("=" * 80)
    return merged

if __name__ == "__main__":
    build_bowler_intelligence()

