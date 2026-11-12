"""
RR PRESSURE INDEX 2027 — PHASE 02.1: BASELINE ENGINE V2
Context-Adjusted Baseline Modelling & Phase-Mix Confounding Elimination.

Key Features:
- 6 Canonical Contexts: (Innings 1 vs 2) x (Powerplay 1-6, Middle 7-15, Death 16-20)
- Population benchmarks across all 6 contexts
- Player-specific phase-weight distributions under pressure
- Context-expected baseline E[Y | weights]
- Context-adjusted performance delta: Delta_context = Y_pressure - E[Y | weights]
- Confounding gap quantification: Gap = Delta_raw - Delta_context
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
TABLES_DIR = os.path.join(BASE_DIR, "outputs", "tables")
os.makedirs(TABLES_DIR, exist_ok=True)

CONTEXT_LABELS = [
    'Inn1_PP', 'Inn1_Mid', 'Inn1_Death',
    'Inn2_PP', 'Inn2_Mid', 'Inn2_Death'
]

def assign_canonical_context(df):
    """
    Assigns each delivery to one of 6 canonical match phases.
    """
    cond_list = [
        (df['is_super_over']),
        (df['innings'] == 1) & (df['overid'] <= 6),
        (df['innings'] == 1) & (df['overid'] > 6) & (df['overid'] <= 15),
        (df['innings'] == 1) & (df['overid'] > 15),
        (df['innings'] == 2) & (df['overid'] <= 6),
        (df['innings'] == 2) & (df['overid'] > 6) & (df['overid'] <= 15),
        (df['innings'] == 2) & (df['overid'] > 15),
    ]
    choice_list = [
        'Super_Over',
        'Inn1_PP', 'Inn1_Mid', 'Inn1_Death',
        'Inn2_PP', 'Inn2_Mid', 'Inn2_Death'
    ]
    return np.select(cond_list, choice_list, default='Other')

def compute_population_benchmarks(df):
    """
    Computes population-wide cricketing metrics across the canonical contexts.
    """
    print("\nComputing Population Benchmarks across Canonical Contexts...")
    
    # Batting population metrics (legal deliveries faced by batter: extras_type != wide)
    df_bat = df[df['extras_type'] != 'wide'].copy()
    bat_pop = df_bat.groupby('context').agg(
        total_balls=('innings_ball_num', 'count'),
        total_runs=('runs', 'sum'),
        boundaries=('runs', lambda s: (s.isin([4, 6])).sum()),
        dots=('runs', lambda s: (s == 0).sum()),
        dismissals=('is_wicket', 'sum')
    ).reset_index()
    
    bat_pop['pop_bat_sr'] = (bat_pop['total_runs'] / bat_pop['total_balls']) * 100.0
    bat_pop['pop_bat_boundary_pct'] = bat_pop['boundaries'] / bat_pop['total_balls']
    bat_pop['pop_bat_dot_pct'] = bat_pop['dots'] / bat_pop['total_balls']
    bat_pop['pop_bat_dismissal_pct'] = bat_pop['dismissals'] / bat_pop['total_balls']

    # Bowling population metrics (legal deliveries bowled: is_legal == True)
    df_bowl = df[df['is_legal']].copy()
    bowl_pop = df_bowl.groupby('context').agg(
        total_balls=('innings_ball_num', 'count'),
        total_runs_conceded=('bowler_runs_conceded', 'sum'),
        boundaries_conceded=('runs', lambda s: (s.isin([4, 6])).sum()),
        dots_bowled=('bowler_runs_conceded', lambda s: (s == 0).sum()),
        wickets=('is_bowler_wicket', 'sum')
    ).reset_index()
    
    bowl_pop['pop_bowl_econ'] = (bowl_pop['total_runs_conceded'] / bowl_pop['total_balls']) * 6.0
    bowl_pop['pop_bowl_boundary_pct'] = bowl_pop['boundaries_conceded'] / bowl_pop['total_balls']
    bowl_pop['pop_bowl_dot_pct'] = bowl_pop['dots_bowled'] / bowl_pop['total_balls']
    bowl_pop['pop_bowl_wicket_pct'] = bowl_pop['wickets'] / bowl_pop['total_balls']

    pop_bench = pd.merge(
        bat_pop[['context', 'total_balls', 'pop_bat_sr', 'pop_bat_boundary_pct', 'pop_bat_dot_pct', 'pop_bat_dismissal_pct']],
        bowl_pop[['context', 'pop_bowl_econ', 'pop_bowl_boundary_pct', 'pop_bowl_dot_pct', 'pop_bowl_wicket_pct']],
        on='context', how='outer'
    )
    
    # Save table
    out_path = os.path.join(TABLES_DIR, "context_population_benchmarks.csv")
    pop_bench.to_csv(out_path, index=False)
    print(f"  Population benchmarks saved to: {out_path}")
    print(pop_bench.to_string(index=False))
    return pop_bench

def build_context_adjusted_baselines():
    print("=" * 80)
    print("RR PRESSURE INDEX 2027 — BASELINE ENGINE V2: CONTEXT-ADJUSTED MODELLING")
    print("=" * 80)

    # 1. Load Hardened Features
    features_path = os.path.join(TABLES_DIR, "delivery_pressure_features_v2.csv")
    print(f"\n[Step 1/5] Loading delivery feature store from: {features_path}")
    df = pd.read_csv(features_path, low_memory=False)
    
    # Player names mapping
    p_map = pd.read_csv(os.path.join(RAW_DIR, "competition_team_player_mapping.csv"))
    id_to_name = p_map.groupby('player_id')['player_name'].last().to_dict()

    # Assign canonical context
    df['context'] = assign_canonical_context(df)

    # 2. Population Benchmarks
    pop_bench = compute_population_benchmarks(df)
    pop_bench_map = pop_bench.set_index('context').to_dict(orient='index')

    # Global population fallbacks
    all_bat_legal = df[df['extras_type'] != 'wide']
    global_bat_sr = (all_bat_legal['runs'].sum() / len(all_bat_legal)) * 100.0
    global_bat_bound = (all_bat_legal['runs'].isin([4, 6])).mean()
    global_bat_dot = (all_bat_legal['runs'] == 0).mean()
    global_bat_dismiss = all_bat_legal['is_wicket'].mean()

    all_bowl_legal = df[df['is_legal']]
    global_bowl_econ = (all_bowl_legal['bowler_runs_conceded'].sum() / len(all_bowl_legal)) * 6.0
    global_bowl_bound = (all_bowl_legal['runs'].isin([4, 6])).mean()
    global_bowl_dot = (all_bowl_legal['bowler_runs_conceded'] == 0).mean()
    global_bowl_wicket = all_bowl_legal['is_bowler_wicket'].mean()

    # -------------------------------------------------------------
    # 3. BATTING CONTEXT-ADJUSTED BASELINES
    # -------------------------------------------------------------
    print("\n[Step 3/5] Computing Batting Context-Adjusted Baselines...")
    df_bat = df[df['extras_type'] != 'wide'].copy()
    
    bat_records = []
    unique_batters = df_bat['striker_id'].unique()

    for b_id in unique_batters:
        b_df = df_bat[df_bat['striker_id'] == b_id]
        total_balls = len(b_df)
        if total_balls < 10:  # Skip trivial appearances
            continue

        b_name = id_to_name.get(b_id, b_df['striker_name'].iloc[0] if pd.notna(b_df['striker_name'].iloc[0]) else f"Batter_{b_id}")
        
        # Partitions
        norm_df = b_df[b_df['is_bat_normal']]
        press_df = b_df[b_df['is_bat_pressure']]
        
        n_norm = len(norm_df)
        n_press = len(press_df)

        # Raw Normal Metrics
        if n_norm > 0:
            norm_sr = (norm_df['runs'].sum() / n_norm) * 100.0
            norm_bound_pct = (norm_df['runs'].isin([4, 6])).mean()
            norm_dot_pct = (norm_df['runs'] == 0).mean()
            norm_dismiss_pct = norm_df['is_wicket'].mean()
        else:
            norm_sr = np.nan
            norm_bound_pct = np.nan
            norm_dot_pct = np.nan
            norm_dismiss_pct = np.nan

        # Raw Pressure Metrics
        if n_press > 0:
            press_sr = (press_df['runs'].sum() / n_press) * 100.0
            press_bound_pct = (press_df['runs'].isin([4, 6])).mean()
            press_dot_pct = (press_df['runs'] == 0).mean()
            press_dismiss_pct = press_df['is_wicket'].mean()
            
            # Phase weights under pressure
            press_ctx_counts = press_df['context'].value_counts()
            w_dict = {c: press_ctx_counts.get(c, 0) / float(n_press) for c in CONTEXT_LABELS}
            
            # Context-Expected Baselines E[Y | pressure context distribution]
            exp_sr = sum(w_dict[c] * pop_bench_map.get(c, {}).get('pop_bat_sr', global_bat_sr) for c in CONTEXT_LABELS)
            exp_bound_pct = sum(w_dict[c] * pop_bench_map.get(c, {}).get('pop_bat_boundary_pct', global_bat_bound) for c in CONTEXT_LABELS)
            exp_dot_pct = sum(w_dict[c] * pop_bench_map.get(c, {}).get('pop_bat_dot_pct', global_bat_dot) for c in CONTEXT_LABELS)
            exp_dismiss_pct = sum(w_dict[c] * pop_bench_map.get(c, {}).get('pop_bat_dismissal_pct', global_bat_dismiss) for c in CONTEXT_LABELS)
            
            # Context-Adjusted Delta
            delta_context_sr = press_sr - exp_sr
            delta_context_bound = press_bound_pct - exp_bound_pct
            delta_context_dot = press_dot_pct - exp_dot_pct
            delta_context_dismiss = press_dismiss_pct - exp_dismiss_pct
            
            # Raw Delta
            delta_raw_sr = press_sr - norm_sr if pd.notna(norm_sr) else np.nan
            confounding_gap_sr = delta_raw_sr - delta_context_sr if pd.notna(delta_raw_sr) else np.nan
            
            death_pct_press = w_dict['Inn1_Death'] + w_dict['Inn2_Death']
            pp_pct_press = w_dict['Inn1_PP'] + w_dict['Inn2_PP']
        else:
            press_sr = np.nan
            press_bound_pct = np.nan
            press_dot_pct = np.nan
            press_dismiss_pct = np.nan
            exp_sr = np.nan
            exp_bound_pct = np.nan
            exp_dot_pct = np.nan
            exp_dismiss_pct = np.nan
            delta_context_sr = np.nan
            delta_context_bound = np.nan
            delta_context_dot = np.nan
            delta_context_dismiss = np.nan
            delta_raw_sr = np.nan
            confounding_gap_sr = np.nan
            death_pct_press = 0.0
            pp_pct_press = 0.0

        bat_records.append({
            'role': 'batter',
            'player_id': b_id,
            'player_name': b_name,
            'total_balls': total_balls,
            'normal_balls': n_norm,
            'pressure_balls': n_press,
            'pressure_share': n_press / total_balls if total_balls > 0 else 0.0,
            'death_pressure_share': death_pct_press,
            'pp_pressure_share': pp_pct_press,
            # Normal empirical
            'norm_sr': norm_sr,
            'norm_boundary_pct': norm_bound_pct,
            'norm_dot_pct': norm_dot_pct,
            'norm_dismissal_pct': norm_dismiss_pct,
            # Pressure empirical
            'press_sr': press_sr,
            'press_boundary_pct': press_bound_pct,
            'press_dot_pct': press_dot_pct,
            'press_dismissal_pct': press_dismiss_pct,
            # Context-expected benchmark
            'exp_sr': exp_sr,
            'exp_boundary_pct': exp_bound_pct,
            'exp_dot_pct': exp_dot_pct,
            'exp_dismissal_pct': exp_dismiss_pct,
            # Context-adjusted deltas
            'delta_context_sr': delta_context_sr,
            'delta_context_boundary_pct': delta_context_bound,
            'delta_context_dot_pct': delta_context_dot,
            'delta_context_dismissal_pct': delta_context_dismiss,
            # Raw delta & confounding gap
            'delta_raw_sr': delta_raw_sr,
            'confounding_gap_sr': confounding_gap_sr
        })

    df_bat_adj = pd.DataFrame(bat_records)
    print(f"  Processed {len(df_bat_adj)} batters.")

    # -------------------------------------------------------------
    # 4. BOWLING CONTEXT-ADJUSTED BASELINES
    # -------------------------------------------------------------
    print("\n[Step 4/5] Computing Bowling Context-Adjusted Baselines...")
    df_bowl = df[df['is_legal']].copy()
    
    bowl_records = []
    unique_bowlers = df_bowl['bowler_id'].unique()

    for b_id in unique_bowlers:
        b_df = df_bowl[df_bowl['bowler_id'] == b_id]
        total_balls = len(b_df)
        if total_balls < 12:  # Skip trivial appearances (< 2 overs)
            continue

        b_name = id_to_name.get(b_id, b_df['bowler_name'].iloc[0] if pd.notna(b_df['bowler_name'].iloc[0]) else f"Bowler_{b_id}")
        
        # Partitions
        norm_df = b_df[b_df['is_bowl_normal']]
        leverage_df = b_df[b_df['is_bowl_leverage']]
        
        n_norm = len(norm_df)
        n_lev = len(leverage_df)

        # Raw Normal Metrics
        if n_norm > 0:
            norm_econ = (norm_df['bowler_runs_conceded'].sum() / n_norm) * 6.0
            norm_bound_pct = (norm_df['runs'].isin([4, 6])).mean()
            norm_dot_pct = (norm_df['bowler_runs_conceded'] == 0).mean()
            norm_wicket_pct = norm_df['is_bowler_wicket'].mean()
        else:
            norm_econ = np.nan
            norm_bound_pct = np.nan
            norm_dot_pct = np.nan
            norm_wicket_pct = np.nan

        # Raw Leverage Metrics
        if n_lev > 0:
            lev_econ = (leverage_df['bowler_runs_conceded'].sum() / n_lev) * 6.0
            lev_bound_pct = (leverage_df['runs'].isin([4, 6])).mean()
            lev_dot_pct = (leverage_df['bowler_runs_conceded'] == 0).mean()
            lev_wicket_pct = leverage_df['is_bowler_wicket'].mean()
            
            # Phase weights under leverage
            lev_ctx_counts = leverage_df['context'].value_counts()
            w_dict = {c: lev_ctx_counts.get(c, 0) / float(n_lev) for c in CONTEXT_LABELS}
            
            # Context-Expected Baselines E[Y | leverage context distribution]
            exp_econ = sum(w_dict[c] * pop_bench_map.get(c, {}).get('pop_bowl_econ', global_bowl_econ) for c in CONTEXT_LABELS)
            exp_bound_pct = sum(w_dict[c] * pop_bench_map.get(c, {}).get('pop_bowl_boundary_pct', global_bowl_bound) for c in CONTEXT_LABELS)
            exp_dot_pct = sum(w_dict[c] * pop_bench_map.get(c, {}).get('pop_bowl_dot_pct', global_bowl_dot) for c in CONTEXT_LABELS)
            exp_wicket_pct = sum(w_dict[c] * pop_bench_map.get(c, {}).get('pop_bowl_wicket_pct', global_bowl_wicket) for c in CONTEXT_LABELS)
            
            # Context-Adjusted Delta (for economy & boundary%, negative is good; for dot & wicket%, positive is good)
            delta_context_econ = lev_econ - exp_econ
            delta_context_bound = lev_bound_pct - exp_bound_pct
            delta_context_dot = lev_dot_pct - exp_dot_pct
            delta_context_wicket = lev_wicket_pct - exp_wicket_pct
            
            # Raw Delta
            delta_raw_econ = lev_econ - norm_econ if pd.notna(norm_econ) else np.nan
            confounding_gap_econ = delta_raw_econ - delta_context_econ if pd.notna(delta_raw_econ) else np.nan
            
            death_pct_lev = w_dict['Inn1_Death'] + w_dict['Inn2_Death']
            pp_pct_lev = w_dict['Inn1_PP'] + w_dict['Inn2_PP']
        else:
            lev_econ = np.nan
            lev_bound_pct = np.nan
            lev_dot_pct = np.nan
            lev_wicket_pct = np.nan
            exp_econ = np.nan
            exp_bound_pct = np.nan
            exp_dot_pct = np.nan
            exp_wicket_pct = np.nan
            delta_context_econ = np.nan
            delta_context_bound = np.nan
            delta_context_dot = np.nan
            delta_context_wicket = np.nan
            delta_raw_econ = np.nan
            confounding_gap_econ = np.nan
            death_pct_lev = 0.0
            pp_pct_lev = 0.0

        bowl_records.append({
            'role': 'bowler',
            'player_id': b_id,
            'player_name': b_name,
            'total_balls': total_balls,
            'normal_balls': n_norm,
            'leverage_balls': n_lev,
            'leverage_share': n_lev / total_balls if total_balls > 0 else 0.0,
            'death_leverage_share': death_pct_lev,
            'pp_leverage_share': pp_pct_lev,
            # Normal empirical
            'norm_econ': norm_econ,
            'norm_boundary_pct': norm_bound_pct,
            'norm_dot_pct': norm_dot_pct,
            'norm_wicket_pct': norm_wicket_pct,
            # Leverage empirical
            'lev_econ': lev_econ,
            'lev_boundary_pct': lev_bound_pct,
            'lev_dot_pct': lev_dot_pct,
            'lev_wicket_pct': lev_wicket_pct,
            # Context-expected benchmark
            'exp_econ': exp_econ,
            'exp_boundary_pct': exp_bound_pct,
            'exp_dot_pct': exp_dot_pct,
            'exp_wicket_pct': exp_wicket_pct,
            # Context-adjusted deltas
            'delta_context_econ': delta_context_econ,
            'delta_context_boundary_pct': delta_context_bound,
            'delta_context_dot_pct': delta_context_dot,
            'delta_context_wicket_pct': delta_context_wicket,
            # Raw delta & confounding gap
            'delta_raw_econ': delta_raw_econ,
            'confounding_gap_econ': confounding_gap_econ
        })

    df_bowl_adj = pd.DataFrame(bowl_records)
    print(f"  Processed {len(df_bowl_adj)} bowlers.")

    # -------------------------------------------------------------
    # 5. MERGE & EXPORT
    # -------------------------------------------------------------
    print("\n[Step 5/5] Consolidating and Exporting Context-Adjusted Baselines...")
    df_combined = pd.concat([df_bat_adj, df_bowl_adj], ignore_index=True)
    out_file = os.path.join(TABLES_DIR, "context_adjusted_baselines.csv")
    df_combined.to_csv(out_file, index=False)
    print(f"  Saved {len(df_combined)} player context-adjusted baselines to: {out_file}")

    # Confounding diagnosis summary
    qual_bat = df_bat_adj[df_bat_adj['pressure_balls'] >= 40].copy()
    qual_bowl = df_bowl_adj[df_bowl_adj['leverage_balls'] >= 60].copy()
    
    print("\nCONFOUNDING DIAGNOSIS SUMMARY:")
    print(f"  Qualified Batters (>= 40 pressure balls): {len(qual_bat)}")
    print(f"  Average Batting Raw Delta SR: {qual_bat['delta_raw_sr'].mean():.2f}")
    print(f"  Average Batting Context-Adjusted Delta SR: {qual_bat['delta_context_sr'].mean():.2f}")
    print(f"  Average Phase Confounding Gap (Raw - Context): {qual_bat['confounding_gap_sr'].mean():.2f} SR points")
    print(f"  Correlation between Death-Overs Share and Raw Delta SR: {qual_bat['death_pressure_share'].corr(qual_bat['delta_raw_sr']):.3f}")
    print(f"  Correlation between Death-Overs Share and Context Delta SR: {qual_bat['death_pressure_share'].corr(qual_bat['delta_context_sr']):.3f}")

    print(f"\n  Qualified Bowlers (>= 60 leverage balls): {len(qual_bowl)}")
    print(f"  Average Bowling Raw Delta Econ: {qual_bowl['delta_raw_econ'].mean():.2f}")
    print(f"  Average Bowling Context-Adjusted Delta Econ: {qual_bowl['delta_context_econ'].mean():.2f}")
    print(f"  Average Phase Confounding Gap (Raw - Context): {qual_bowl['confounding_gap_econ'].mean():.2f} rpo")
    print("=" * 80)

    return df_combined

if __name__ == "__main__":
    build_context_adjusted_baselines()
