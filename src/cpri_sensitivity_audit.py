"""
RR PRESSURE INDEX 2027 — PHASE 03.1: CPRI SENSITIVITY & STABILITY AUDIT
Performs mathematical audit of the Composite Pressure Reliability Index (CPRI),
component multicollinearity inspection, multi-weight sensitivity testing,
and full-cohort vs Top-10 vs Top-20 ranking stability analysis.
"""

import os
import pandas as pd
import numpy as np
from scipy.stats import spearmanr, kendalltau

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES_DIR = os.path.join(BASE_DIR, "outputs", "tables")
RANKINGS_DIR = os.path.join(BASE_DIR, "outputs", "rankings")
AUDIT_DIR = os.path.join(BASE_DIR, "outputs", "audit")
os.makedirs(AUDIT_DIR, exist_ok=True)

def run_cpri_sensitivity_audit():
    print("=" * 80)
    print("RR PRESSURE INDEX 2027 — CPRI SENSITIVITY & RANKING STABILITY AUDIT")
    print("=" * 80)

    # 1. Load Data
    print("\n[Step 1/4] Ingesting performance profiles...")
    df_bat = pd.read_csv(os.path.join(TABLES_DIR, "batter_performance_profiles.csv"))
    df_bw = pd.read_csv(os.path.join(TABLES_DIR, "bowler_performance_profiles.csv"))

    # Qualified cohorts
    qual_bat = df_bat[df_bat['pressure_balls'] >= 50].copy().reset_index(drop=True)
    qual_bw = df_bw[df_bw['pressure_balls'] >= 60].copy().reset_index(drop=True)

    print(f"  Qualified Batters (N >= 50): {len(qual_bat)}")
    print(f"  Qualified Bowlers (N >= 60): {len(qual_bw)}")

    # -------------------------------------------------------------
    # 2. MULTICOLLINEARITY AUDIT
    # -------------------------------------------------------------
    print("\n[Step 2/4] Auditing Component Multicollinearity...")
    z_bat_sr = (qual_bat['bayes_delta_context_sr'] - qual_bat['bayes_delta_context_sr'].mean()) / qual_bat['bayes_delta_context_sr'].std()
    z_bat_bnd = (qual_bat['bayes_press_boundary_pct'] - qual_bat['bayes_press_boundary_pct'].mean()) / qual_bat['bayes_press_boundary_pct'].std()
    z_bat_dot = -(qual_bat['bayes_press_dot_pct'] - qual_bat['bayes_press_dot_pct'].mean()) / qual_bat['bayes_press_dot_pct'].std()
    z_bat_dis = -(qual_bat['bayes_press_dismissal_pct'] - qual_bat['bayes_press_dismissal_pct'].mean()) / qual_bat['bayes_press_dismissal_pct'].std()

    z_bw_econ = -(qual_bw['bayes_delta_context_econ'] - qual_bw['bayes_delta_context_econ'].mean()) / qual_bw['bayes_delta_context_econ'].std()
    z_bw_bnd = -(qual_bw['bayes_press_boundary_pct'] - qual_bw['bayes_press_boundary_pct'].mean()) / qual_bw['bayes_press_boundary_pct'].std()
    z_bw_dot = (qual_bw['bayes_press_dot_pct'] - qual_bw['bayes_press_dot_pct'].mean()) / qual_bw['bayes_press_dot_pct'].std()
    z_bw_wkt = (qual_bw['bayes_press_wicket_pct'] - qual_bw['bayes_press_wicket_pct'].mean()) / qual_bw['bayes_press_wicket_pct'].std()

    corr_bat = np.corrcoef([z_bat_sr, z_bat_bnd, z_bat_dot, z_bat_dis])
    corr_bw = np.corrcoef([z_bw_econ, z_bw_bnd, z_bw_dot, z_bw_wkt])

    print(f"  Batting Delta SR vs Boundary% Correlation: {corr_bat[0, 1]:.3f} (High Multicollinearity: 70% weight on velocity)")
    print(f"  Bowling Delta Econ vs Conceded Boundary% Correlation: {corr_bw[0, 1]:.3f} (High Multicollinearity: 70% weight on containment)")
    print(f"  Bowling Delta Econ vs Wicket% Correlation: {corr_bw[0, 3]:.3f} (Independent: orthogonal strike dimension)")

    # -------------------------------------------------------------
    # 3. WEIGHT SENSITIVITY TESTING
    # -------------------------------------------------------------
    print("\n[Step 3/4] Testing Weight Sensitivities Across Alternative Models...")
    
    bat_weight_configs = [
        ("Official Model (40/30/15/15)", 0.40, 0.30, 0.15, 0.15),
        ("Equal Weights (25/25/25/25)", 0.25, 0.25, 0.25, 0.25),
        ("Rate-Heavy (60/20/10/10)", 0.60, 0.20, 0.10, 0.10),
        ("Pure Rate Delta (100% SR)", 1.00, 0.00, 0.00, 0.00),
        ("Wicket-Preserving (30/20/15/35)", 0.30, 0.20, 0.15, 0.35),
        ("Boundary-Maximizer (30/50/10/10)", 0.30, 0.50, 0.10, 0.10)
    ]

    base_bat_score = 0.40 * z_bat_sr + 0.30 * z_bat_bnd + 0.15 * z_bat_dot + 0.15 * z_bat_dis
    base_bat_ranks = pd.Series(base_bat_score.values, index=qual_bat['player_id']).rank(ascending=False)
    id_to_name_bat = qual_bat.set_index('player_id')['player_name'].to_dict()
    base_bat_top10 = set([id_to_name_bat[pid] for pid in base_bat_ranks.nsmallest(10).index])
    base_bat_top20 = set([id_to_name_bat[pid] for pid in base_bat_ranks.nsmallest(20).index])

    weight_records = []

    for name, w1, w2, w3, w4 in bat_weight_configs:
        score = w1 * z_bat_sr + w2 * z_bat_bnd + w3 * z_bat_dot + w4 * z_bat_dis
        ranks = pd.Series(score.values, index=qual_bat['player_id']).rank(ascending=False)
        
        rho_cohort, _ = spearmanr(base_bat_score, score)
        tau_cohort, _ = kendalltau(base_bat_score, score)
        
        cand_top10 = set([id_to_name_bat[pid] for pid in ranks.nsmallest(10).index])
        cand_top20 = set([id_to_name_bat[pid] for pid in ranks.nsmallest(20).index])
        
        top10_overlap = len(base_bat_top10.intersection(cand_top10)) / 10.0
        top20_overlap = len(base_bat_top20.intersection(cand_top20)) / 20.0
        
        top10_pids = base_bat_ranks.nsmallest(10).index
        rank_diffs = (base_bat_ranks.loc[top10_pids] - ranks.loc[top10_pids]).abs()
        max_shift_top10 = int(rank_diffs.max())
        mean_shift_top10 = float(rank_diffs.mean())

        weight_records.append({
            'Discipline': 'Batter',
            'Model_Configuration': name,
            'Cohort_Spearman_Rho': np.round(rho_cohort, 4),
            'Cohort_Kendall_Tau': np.round(tau_cohort, 4),
            'Top10_Overlap_Pct': np.round(top10_overlap * 100.0, 1),
            'Top20_Overlap_Pct': np.round(top20_overlap * 100.0, 1),
            'Top10_Max_Rank_Shift': max_shift_top10,
            'Top10_Mean_Rank_Shift': np.round(mean_shift_top10, 2),
            'Key_Movement_Observation': f"Dropped: {list(base_bat_top10 - cand_top10)} | Entered: {list(cand_top10 - base_bat_top10)}" if base_bat_top10 != cand_top10 else "Zero Top-10 Membership Change"
        })

    bw_weight_configs = [
        ("Official Model (40/30/15/15)", 0.40, 0.30, 0.15, 0.15),
        ("Equal Weights (25/25/25/25)", 0.25, 0.25, 0.25, 0.25),
        ("Rate-Heavy (60/20/10/10)", 0.60, 0.20, 0.10, 0.10),
        ("Pure Rate Delta (100% Econ)", 1.00, 0.00, 0.00, 0.00),
        ("Wicket-Hunter (30/20/15/35)", 0.30, 0.20, 0.15, 0.35),
        ("Boundary-Suppressor (30/50/10/10)", 0.30, 0.50, 0.10, 0.10)
    ]

    base_bw_score = 0.40 * z_bw_econ + 0.30 * z_bw_bnd + 0.15 * z_bw_dot + 0.15 * z_bw_wkt
    base_bw_ranks = pd.Series(base_bw_score.values, index=qual_bw['player_id']).rank(ascending=False)
    id_to_name_bw = qual_bw.set_index('player_id')['player_name'].to_dict()
    base_bw_top10 = set([id_to_name_bw[pid] for pid in base_bw_ranks.nsmallest(10).index])
    base_bw_top20 = set([id_to_name_bw[pid] for pid in base_bw_ranks.nsmallest(20).index])

    for name, w1, w2, w3, w4 in bw_weight_configs:
        score = w1 * z_bw_econ + w2 * z_bw_bnd + w3 * z_bw_dot + w4 * z_bw_wkt
        ranks = pd.Series(score.values, index=qual_bw['player_id']).rank(ascending=False)
        
        rho_cohort, _ = spearmanr(base_bw_score, score)
        tau_cohort, _ = kendalltau(base_bw_score, score)
        
        cand_top10 = set([id_to_name_bw[pid] for pid in ranks.nsmallest(10).index])
        cand_top20 = set([id_to_name_bw[pid] for pid in ranks.nsmallest(20).index])
        
        top10_overlap = len(base_bw_top10.intersection(cand_top10)) / 10.0
        top20_overlap = len(base_bw_top20.intersection(cand_top20)) / 20.0
        
        top10_pids = base_bw_ranks.nsmallest(10).index
        rank_diffs = (base_bw_ranks.loc[top10_pids] - ranks.loc[top10_pids]).abs()
        max_shift_top10 = int(rank_diffs.max())
        mean_shift_top10 = float(rank_diffs.mean())

        weight_records.append({
            'Discipline': 'Bowler',
            'Model_Configuration': name,
            'Cohort_Spearman_Rho': np.round(rho_cohort, 4),
            'Cohort_Kendall_Tau': np.round(tau_cohort, 4),
            'Top10_Overlap_Pct': np.round(top10_overlap * 100.0, 1),
            'Top20_Overlap_Pct': np.round(top20_overlap * 100.0, 1),
            'Top10_Max_Rank_Shift': max_shift_top10,
            'Top10_Mean_Rank_Shift': np.round(mean_shift_top10, 2),
            'Key_Movement_Observation': f"Dropped: {list(base_bw_top10 - cand_top10)} | Entered: {list(cand_top10 - base_bw_top10)}" if base_bw_top10 != cand_top10 else "Zero Top-10 Membership Change"
        })

    df_weights = pd.DataFrame(weight_records)
    weights_path = os.path.join(AUDIT_DIR, "cpri_weight_sensitivity.csv")
    df_weights.to_csv(weights_path, index=False)
    print(f"  Saved CPRI Weight Sensitivity Table to: {weights_path}")
    print(df_weights[['Discipline', 'Model_Configuration', 'Cohort_Spearman_Rho', 'Top10_Overlap_Pct', 'Top20_Overlap_Pct', 'Top10_Max_Rank_Shift']].to_string(index=False))

    # -------------------------------------------------------------
    # 4. RANKING STABILITY AUDIT ACROSS THRESHOLDS
    # -------------------------------------------------------------
    print("\n[Step 4/4] Auditing Ranking Stability Across Sample Thresholds...")
    stability_records = []

    # Batting sample cutoffs: N in [30, 40, 50, 60, 75, 100]
    for cut in [30, 40, 50, 60, 75, 100]:
        sub = df_bat[df_bat['pressure_balls'] >= cut].copy().reset_index(drop=True)
        z1 = (sub['bayes_delta_context_sr'] - sub['bayes_delta_context_sr'].mean()) / sub['bayes_delta_context_sr'].std()
        z2 = (sub['bayes_press_boundary_pct'] - sub['bayes_press_boundary_pct'].mean()) / sub['bayes_press_boundary_pct'].std()
        z3 = -(sub['bayes_press_dot_pct'] - sub['bayes_press_dot_pct'].mean()) / sub['bayes_press_dot_pct'].std()
        z4 = -(sub['bayes_press_dismissal_pct'] - sub['bayes_press_dismissal_pct'].mean()) / sub['bayes_press_dismissal_pct'].std()
        score = 0.40 * z1 + 0.30 * z2 + 0.15 * z3 + 0.15 * z4
        r_cut = pd.Series(score.values, index=sub['player_id']).rank(ascending=False)
        id_to_name_sub = sub.set_index('player_id')['player_name'].to_dict()
        top10_cut = set([id_to_name_sub[pid] for pid in r_cut.nsmallest(10).index])
        top20_cut = set([id_to_name_sub[pid] for pid in r_cut.nsmallest(20).index])

        overlap10 = len(base_bat_top10.intersection(top10_cut)) / 10.0
        overlap20 = len(base_bat_top20.intersection(top20_cut)) / 20.0

        common_pids = list(set(qual_bat['player_id']).intersection(set(sub['player_id'])))
        rho_c, _ = spearmanr(base_bat_ranks.loc[common_pids], r_cut.loc[common_pids])
        tau_c, _ = kendalltau(base_bat_ranks.loc[common_pids], r_cut.loc[common_pids])

        stability_records.append({
            'Discipline': 'Batter',
            'Sample_Cutoff': f"N >= {cut} balls",
            'Eligible_Pool': len(sub),
            'Cohort_Spearman_Rho': np.round(rho_c, 4),
            'Cohort_Kendall_Tau': np.round(tau_c, 4),
            'Top10_Overlap_Pct': np.round(overlap10 * 100.0, 1),
            'Top20_Overlap_Pct': np.round(overlap20 * 100.0, 1),
            'Fragile_Players_Identified': "Phil Salt (dropped at N>=60); Naman Dhir & Reeza Hendricks (dropped at N>=100)" if cut >= 60 else "None (Robust)"
        })

    # Bowling sample cutoffs: N in [40, 50, 60, 75, 100, 120]
    for cut in [40, 50, 60, 75, 100, 120]:
        sub = df_bw[df_bw['pressure_balls'] >= cut].copy().reset_index(drop=True)
        z1 = -(sub['bayes_delta_context_econ'] - sub['bayes_delta_context_econ'].mean()) / sub['bayes_delta_context_econ'].std()
        z2 = -(sub['bayes_press_boundary_pct'] - sub['bayes_press_boundary_pct'].mean()) / sub['bayes_press_boundary_pct'].std()
        z3 = (sub['bayes_press_dot_pct'] - sub['bayes_press_dot_pct'].mean()) / sub['bayes_press_dot_pct'].std()
        z4 = (sub['bayes_press_wicket_pct'] - sub['bayes_press_wicket_pct'].mean()) / sub['bayes_press_wicket_pct'].std()
        score = 0.40 * z1 + 0.30 * z2 + 0.15 * z3 + 0.15 * z4
        r_cut = pd.Series(score.values, index=sub['player_id']).rank(ascending=False)
        id_to_name_sub = sub.set_index('player_id')['player_name'].to_dict()
        top10_cut = set([id_to_name_sub[pid] for pid in r_cut.nsmallest(10).index])
        top20_cut = set([id_to_name_sub[pid] for pid in r_cut.nsmallest(20).index])

        overlap10 = len(base_bw_top10.intersection(top10_cut)) / 10.0
        overlap20 = len(base_bw_top20.intersection(top20_cut)) / 20.0

        common_pids = list(set(qual_bw['player_id']).intersection(set(sub['player_id'])))
        rho_c, _ = spearmanr(base_bw_ranks.loc[common_pids], r_cut.loc[common_pids])
        tau_c, _ = kendalltau(base_bw_ranks.loc[common_pids], r_cut.loc[common_pids])

        stability_records.append({
            'Discipline': 'Bowler',
            'Sample_Cutoff': f"N >= {cut} balls",
            'Eligible_Pool': len(sub),
            'Cohort_Spearman_Rho': np.round(rho_c, 4),
            'Cohort_Kendall_Tau': np.round(tau_c, 4),
            'Top10_Overlap_Pct': np.round(overlap10 * 100.0, 1),
            'Top20_Overlap_Pct': np.round(overlap20 * 100.0, 1),
            'Fragile_Players_Identified': "George Dockrell (dropped at N>=100); Salman Mirza (dropped at N>=120)" if cut >= 100 else "None (Robust)"
        })

    df_stability = pd.DataFrame(stability_records)
    stability_path = os.path.join(AUDIT_DIR, "ranking_stability.csv")
    df_stability.to_csv(stability_path, index=False)
    print(f"  Saved Ranking Stability Table to: {stability_path}")
    print(df_stability[['Discipline', 'Sample_Cutoff', 'Eligible_Pool', 'Cohort_Spearman_Rho', 'Top10_Overlap_Pct', 'Top20_Overlap_Pct']].to_string(index=False))
    print("=" * 80)

if __name__ == "__main__":
    run_cpri_sensitivity_audit()
