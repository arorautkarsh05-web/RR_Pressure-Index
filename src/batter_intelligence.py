"""
RR PRESSURE INDEX 2027 — PHASE 03: BATTER INTELLIGENCE ENGINE
Comprehensive Player-Level Analysis for All Eligible Batters.

Calculates:
- Pressure runs, balls faced, strike rate, batting average (runs/dismissals)
- Boundary percentage, dot-ball percentage, dismissal rate
- Context-expected baseline (E[SR], E[Bound%], E[Dot%], E[Dismiss%])
- Context-adjusted delta (Delta_context = Y_pressure - E[Y])
- Normal baseline & raw delta (Delta_raw = Y_pressure - Y_normal)
- Phase confounding gap (Gap = Delta_raw - Delta_context)
- Match-level consistency (standard deviation, CV, and success rate)
- Bayesian posteriors & exact 95% Credible Intervals (Beta-Binomial & Clustered Normal-Normal)
- Specialized contextual metrics:
  * Chasing Clutch (CCI): Innings 2 pressure balls
  * Collapse Recovery (CRI): Overs 1-12, wickets lost >= 3, collapse strain >= 0.40
  * Death Finishing (DEI): Overs 16-20 pressure balls
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES_DIR = os.path.join(BASE_DIR, "outputs", "tables")
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(TABLES_DIR, exist_ok=True)

def build_batter_intelligence():
    print("=" * 80)
    print("RR PRESSURE INDEX 2027 — BATTER INTELLIGENCE ENGINE")
    print("=" * 80)

    # 1. Load Data
    features_path = os.path.join(TABLES_DIR, "delivery_pressure_features_v2.csv")
    base_path = os.path.join(TABLES_DIR, "context_adjusted_baselines.csv")
    bayes_path = os.path.join(TABLES_DIR, "bayesian_model_comparison.csv")
    
    print(f"\n[Step 1/5] Loading feature store from: {features_path}")
    df_del = pd.read_csv(features_path, low_memory=False)
    df_base = pd.read_csv(base_path)
    df_bayes = pd.read_csv(bayes_path)
    
    # Filter legal deliveries faced by batter (extras_type != 'wide')
    df_bat_del = df_del[df_del['extras_type'] != 'wide'].copy()
    print(f"  Total Batting Legal Balls Faced: {len(df_bat_del):,}")

    # Vectorized flags
    df_bat_del['press_ball_flag'] = df_bat_del['is_bat_pressure'].astype(int)
    df_bat_del['press_runs_val'] = np.where(df_bat_del['is_bat_pressure'], df_bat_del['runs'], 0)
    df_bat_del['press_outs_val'] = np.where(df_bat_del['is_bat_pressure'] & df_bat_del['is_wicket'], 1, 0)

    # 2. Match-Level Aggregate for Consistency Analysis
    print("\n[Step 2/5] Computing Match-Level Batting Performance & Consistency Metrics...")
    m_bat = df_bat_del.groupby(['match_id', 'striker_id']).agg(
        match_balls=('innings_ball_num', 'count'),
        match_runs=('runs', 'sum'),
        match_pressure_balls=('press_ball_flag', 'sum'),
        match_pressure_runs=('press_runs_val', 'sum'),
        match_pressure_outs=('press_outs_val', 'sum')
    ).reset_index()

    m_bat['match_press_sr'] = np.where(
        m_bat['match_pressure_balls'] > 0,
        (m_bat['match_pressure_runs'] / m_bat['match_pressure_balls']) * 100.0,
        np.nan
    )

    # Match-level consistency per batter
    bat_consistency = []
    for pid, grp in m_bat.groupby('striker_id'):
        p_grp = grp[grp['match_pressure_balls'] >= 5]  # Matches with meaningful pressure exposure
        n_press_matches = len(p_grp)
        if n_press_matches >= 3:
            sr_std = float(p_grp['match_press_sr'].std())
            sr_mean = float(p_grp['match_press_sr'].mean())
            sr_cv = float(sr_std / sr_mean) if sr_mean > 0 else np.nan
            success_rate = float((p_grp['match_press_sr'] >= 140.0).mean())
        else:
            sr_std = np.nan
            sr_cv = np.nan
            success_rate = np.nan
            
        bat_consistency.append({
            'player_id': pid,
            'total_matches_played': grp['match_id'].nunique(),
            'pressure_matches_count': (grp['match_pressure_balls'] > 0).sum(),
            'qualified_pressure_matches': n_press_matches,
            'match_sr_std': sr_std,
            'match_sr_cv': sr_cv,
            'match_success_rate_140': success_rate
        })
    df_consistency = pd.DataFrame(bat_consistency)

    # 3. Contextual Subsets (Chasing Clutch, Collapse Recovery, Death Finishing)
    print("\n[Step 3/5] Computing Specialized Contextual Partitions (CCI, CRI, DEI)...")
    
    # Chasing Clutch: Innings 2 pressure balls
    cci_df = df_bat_del[df_bat_del['is_bat_chasing_clutch']].groupby('striker_id').agg(
        chase_press_balls=('innings_ball_num', 'count'),
        chase_press_runs=('runs', 'sum'),
        chase_press_boundaries=('runs', lambda s: (s.isin([4, 6])).sum()),
        chase_press_dots=('runs', lambda s: (s == 0).sum()),
        chase_press_outs=('is_wicket', 'sum')
    ).reset_index().rename(columns={'striker_id': 'player_id'})
    cci_df['chase_press_sr'] = (cci_df['chase_press_runs'] / cci_df['chase_press_balls']) * 100.0
    cci_df['chase_press_avg'] = np.where(cci_df['chase_press_outs'] > 0, cci_df['chase_press_runs'] / cci_df['chase_press_outs'], cci_df['chase_press_runs'])

    # Collapse Recovery: overs 1-12, wickets lost >= 3, collapse_strain >= 0.40
    cri_df = df_bat_del[df_bat_del['is_collapse_crisis']].groupby('striker_id').agg(
        collapse_balls=('innings_ball_num', 'count'),
        collapse_runs=('runs', 'sum'),
        collapse_boundaries=('runs', lambda s: (s.isin([4, 6])).sum()),
        collapse_dots=('runs', lambda s: (s == 0).sum()),
        collapse_outs=('is_wicket', 'sum')
    ).reset_index().rename(columns={'striker_id': 'player_id'})
    cri_df['collapse_sr'] = (cri_df['collapse_runs'] / cri_df['collapse_balls']) * 100.0
    cri_df['collapse_avg'] = np.where(cri_df['collapse_outs'] > 0, cri_df['collapse_runs'] / cri_df['collapse_outs'], cri_df['collapse_runs'])

    # Death Finishing: overs 16-20 pressure balls
    dei_df = df_bat_del[df_bat_del['is_death_overs'] & df_bat_del['is_bat_pressure']].groupby('striker_id').agg(
        death_press_balls=('innings_ball_num', 'count'),
        death_press_runs=('runs', 'sum'),
        death_press_boundaries=('runs', lambda s: (s.isin([4, 6])).sum()),
        death_press_dots=('runs', lambda s: (s == 0).sum()),
        death_press_outs=('is_wicket', 'sum')
    ).reset_index().rename(columns={'striker_id': 'player_id'})
    dei_df['death_press_sr'] = (dei_df['death_press_runs'] / dei_df['death_press_balls']) * 100.0
    dei_df['death_press_avg'] = np.where(dei_df['death_press_outs'] > 0, dei_df['death_press_runs'] / dei_df['death_press_outs'], dei_df['death_press_runs'])

    # 4. Integrate Baselines & Bayesian Posteriors
    print("\n[Step 4/5] Merging Context-Adjusted Baselines & Bayesian Posteriors...")
    bat_bayes = df_bayes[df_bayes['role'] == 'batter'].copy()
    bat_base = df_base[df_base['role'] == 'batter'].copy()

    # Pressure aggregate totals
    press_totals = df_bat_del[df_bat_del['is_bat_pressure']].groupby('striker_id').agg(
        press_runs=('runs', 'sum'),
        press_outs=('is_wicket', 'sum')
    ).reset_index().rename(columns={'striker_id': 'player_id'})

    # Competitions played
    comp_played = df_bat_del.groupby('striker_id')['format'].unique().apply(lambda arr: "/".join(sorted(arr))).reset_index().rename(columns={'striker_id': 'player_id', 'format': 'competitions'})

    # Merge sequentially on player_id
    merged = pd.merge(bat_bayes, bat_base[['player_id', 'death_pressure_share', 'pp_pressure_share', 'norm_sr', 'norm_boundary_pct', 'norm_dot_pct', 'norm_dismissal_pct']], on='player_id', how='left')
    merged = pd.merge(merged, press_totals, on='player_id', how='left')
    merged = pd.merge(merged, df_consistency, on='player_id', how='left')
    merged = pd.merge(merged, cci_df, on='player_id', how='left')
    merged = pd.merge(merged, cri_df, on='player_id', how='left')
    merged = pd.merge(merged, dei_df, on='player_id', how='left')
    merged = pd.merge(merged, comp_played, on='player_id', how='left')

    # Derived Batter Metrics
    merged['press_bat_avg'] = np.where(merged['press_outs'] > 0, merged['press_runs'] / merged['press_outs'], merged['press_runs'])
    merged['sample_confidence'] = np.where(
        merged['pressure_balls'] >= 100, 'Tier A (High Confidence: N>=100)',
        np.where(merged['pressure_balls'] >= 50, 'Tier B (Moderate Confidence: 50<=N<100)', 'Tier C (Provisional: N<50)')
    )

    # 5. Export Batter Profiles
    out_path = os.path.join(TABLES_DIR, "batter_performance_profiles.csv")
    merged.to_csv(out_path, index=False)
    print(f"  Successfully exported {len(merged)} batter performance profiles to: {out_path}")
    print("=" * 80)
    return merged

if __name__ == "__main__":
    build_batter_intelligence()
