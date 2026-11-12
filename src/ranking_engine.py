"""
RR PRESSURE INDEX 2027 — PHASE 03: RANKING & AUCTION INTELLIGENCE ENGINE
Computes Composite Pressure Reliability Index (CPRI), 95% Credible Bounds,
generates Top 10 Batters & Bowlers rankings, full cohort rankings, player dossiers,
and visualization charts.
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES_DIR = os.path.join(BASE_DIR, "outputs", "tables")
RANKINGS_DIR = os.path.join(BASE_DIR, "outputs", "rankings")
CHARTS_DIR = os.path.join(BASE_DIR, "outputs", "charts")
DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboard")

os.makedirs(RANKINGS_DIR, exist_ok=True)
os.makedirs(CHARTS_DIR, exist_ok=True)
os.makedirs(DASHBOARD_DIR, exist_ok=True)

SUMMARY_PATH = os.path.join(TABLES_DIR, "pressure_metric_summary.csv")
DELIVERY_FEATURES_PATH = os.path.join(TABLES_DIR, "delivery_pressure_features.csv")

def run_ranking_engine():
    print("=" * 80)
    print("RR PRESSURE INDEX 2027 — RANKING & AUCTION INTELLIGENCE ENGINE")
    print("=" * 80)

    if not os.path.exists(SUMMARY_PATH):
        raise FileNotFoundError(f"Summary metrics not found at {SUMMARY_PATH}. Run reliability_model.py first.")

    df_summary = pd.read_csv(SUMMARY_PATH)
    print(f"Loaded {len(df_summary)} player summary records.")

    # -------------------------------------------------------------
    # 1. BATTING RANKINGS FORMULATION
    # -------------------------------------------------------------
    print("\n[Step 1/6] Ranking Batters on Composite Pressure Reliability Index (CPRI)...")
    df_bat = df_summary[df_summary['role_type'] == 'Batter'].copy()
    
    # Qualification: >= 100 overall balls, >= 50 pressure deliveries
    # (Validated in Phase 02 for high statistical precision: CI width <= 20.5 SR points)
    qual_bat = df_bat[(df_bat['overall_balls'] >= 100) & (df_bat['pressure_balls'] >= 50)].copy()
    
    # Composite Pressure Reliability Index (CPRI)
    # Weights: 40% Chasing Clutch (CCI), 35% Death Execution (DEI), 25% Collapse Recovery (CRI)
    qual_bat['CPRI'] = np.round(
        0.40 * qual_bat['CCI'] + 0.35 * qual_bat['DEI'] + 0.25 * qual_bat['CRI'], 2
    )
    
    # Standard Error of CPRI based on sample size: SE = 15.0 / sqrt(N + 30)
    qual_bat['cpri_se'] = np.round(15.0 / np.sqrt(qual_bat['pressure_balls'] + 30.0), 2)
    qual_bat['CPRI_lower95'] = np.round(qual_bat['CPRI'] - 1.96 * qual_bat['cpri_se'], 2)
    qual_bat['CPRI_upper95'] = np.round(qual_bat['CPRI'] + 1.96 * qual_bat['cpri_se'], 2)
    
    # Rank Batters
    qual_bat = qual_bat.sort_values('CPRI', ascending=False).reset_index(drop=True)
    qual_bat['pressure_rank'] = np.arange(1, len(qual_bat) + 1)
    
    top_10_batters = qual_bat.head(10).copy()
    top_10_bat_path = os.path.join(RANKINGS_DIR, "top_10_batters_reliability.csv")
    
    bat_export_cols = [
        'pressure_rank', 'player_id', 'player_name', 'overall_balls', 'pressure_balls',
        'normal_sr', 'pressure_sr', 'shrunk_pressure_sr', 'delta_sr',
        'overall_bnd_pct', 'pressure_bnd_pct', 'delta_bnd_pct',
        'overall_dot_pct', 'pressure_dot_pct', 'delta_dot_pct',
        'CCI', 'CRI', 'DEI', 'CPRI', 'CPRI_lower95', 'CPRI_upper95', 'cpri_se'
    ]
    top_10_batters[bat_export_cols].to_csv(top_10_bat_path, index=False)
    print(f"  Saved Top 10 Batters to: {top_10_bat_path}")

    # -------------------------------------------------------------
    # 2. BOWLING RANKINGS FORMULATION
    # -------------------------------------------------------------
    print("\n[Step 2/6] Ranking Bowlers on Composite Pressure Reliability Index (CPRI)...")
    df_bw = df_summary[df_summary['role_type'] == 'Bowler'].copy()
    
    # Qualification: >= 100 overall legal balls, >= 50 pressure legal deliveries
    qual_bw = df_bw[(df_bw['overall_legal_balls'] >= 100) & (df_bw['pressure_legal_balls'] >= 50)].copy()
    
    # Composite Pressure Reliability Index (CPRI)
    # Weights: 40% Chasing Defense (CCI), 35% Death Defense (DEI), 25% Collapse Breakthrough (CRI)
    qual_bw['CPRI'] = np.round(
        0.40 * qual_bw['CCI'] + 0.35 * qual_bw['DEI'] + 0.25 * qual_bw['CRI'], 2
    )
    
    qual_bw['cpri_se'] = np.round(15.0 / np.sqrt(qual_bw['pressure_legal_balls'] + 30.0), 2)
    qual_bw['CPRI_lower95'] = np.round(qual_bw['CPRI'] - 1.96 * qual_bw['cpri_se'], 2)
    qual_bw['CPRI_upper95'] = np.round(qual_bw['CPRI'] + 1.96 * qual_bw['cpri_se'], 2)
    
    # Rank Bowlers
    qual_bw = qual_bw.sort_values('CPRI', ascending=False).reset_index(drop=True)
    qual_bw['pressure_rank'] = np.arange(1, len(qual_bw) + 1)
    
    top_10_bowlers = qual_bw.head(10).copy()
    top_10_bw_path = os.path.join(RANKINGS_DIR, "top_10_bowlers_reliability.csv")
    
    bw_export_cols = [
        'pressure_rank', 'player_id', 'player_name', 'overall_legal_balls', 'pressure_legal_balls',
        'normal_econ', 'pressure_econ', 'shrunk_pressure_econ', 'delta_econ',
        'overall_dot_pct', 'pressure_dot_pct', 'delta_dot_pct',
        'overall_bnd_pct', 'pressure_bnd_pct', 'delta_bnd_pct',
        'CCI', 'CRI', 'DEI', 'CPRI', 'CPRI_lower95', 'CPRI_upper95', 'cpri_se'
    ]
    top_10_bowlers[bw_export_cols].to_csv(top_10_bw_path, index=False)
    print(f"  Saved Top 10 Bowlers to: {top_10_bw_path}")

    # Full Player Rankings Table
    full_rankings = pd.concat([qual_bat, qual_bw], ignore_index=True)
    full_rankings_path = os.path.join(RANKINGS_DIR, "full_player_rankings.csv")
    full_rankings.to_csv(full_rankings_path, index=False)
    print(f"  Saved Full Player Rankings to: {full_rankings_path} ({len(full_rankings)} qualified players)")

    # -------------------------------------------------------------
    # 3. DETAILED PLAYER DOSSIERS & SIGNATURE MATCH EVIDENCE
    # -------------------------------------------------------------
    print("\n[Step 3/6] Compiling Forensic Dossiers & Signature Match Evidence...")
    # Load delivery features to extract signature matches
    df_deliv = pd.read_csv(DELIVERY_FEATURES_PATH, low_memory=False)
    
    # For Top 10 Batters
    bat_dossiers = []
    for _, r in top_10_batters.iterrows():
        pid = r['player_id']
        p_deliv = df_deliv[(df_deliv['striker_id'] == pid) & (df_deliv['is_pressure_ball'] == True)]
        
        # Identify match with highest pressure runs scored
        m_perf = p_deliv.groupby(['match_id', 'match_date', 'format']).agg(
            pressure_runs=('runs', 'sum'),
            pressure_balls=('innings_ball_num', 'count')
        ).reset_index().sort_values('pressure_runs', ascending=False)
        
        best_m = m_perf.iloc[0] if len(m_perf) > 0 else None
        sig_str = f"Match {int(best_m['match_id'])} ({best_m['format']}, {best_m['match_date']}): {int(best_m['pressure_runs'])} runs off {int(best_m['pressure_balls'])} pressure balls" if best_m is not None else "N/A"
        
        # Primary pressure archetype
        cci, cri, dei = r['CCI'], r['CRI'], r['DEI']
        if dei == max(cci, cri, dei):
            archetype = "Death Overs Specialist / Finisher"
        elif cci == max(cci, cri, dei):
            archetype = "Chasing Anchor / High-RRR Chaser"
        else:
            archetype = "Collapse Stabilizer & Crisis Rebuilder"
            
        bat_dossiers.append({
            "player_id": pid,
            "player_name": r['player_name'],
            "role": "Batter",
            "pressure_rank": r['pressure_rank'],
            "pressure_archetype": archetype,
            "CPRI_score": r['CPRI'],
            "CPRI_95_CI": f"[{r['CPRI_lower95']:.2f}, {r['CPRI_upper95']:.2f}]",
            "normal_sr": r['normal_sr'],
            "pressure_sr": r['pressure_sr'],
            "delta_sr": r['delta_sr'],
            "CCI": r['CCI'],
            "CRI": r['CRI'],
            "DEI": r['DEI'],
            "pressure_deliveries": int(r['pressure_balls']),
            "signature_match_evidence": sig_str,
            "auction_tier": "Tier 1 - Marquee Clutch Asset" if r['pressure_rank'] <= 5 else "Tier 2 - Premium Situational Asset"
        })

    # For Top 10 Bowlers
    bw_dossiers = []
    for _, r in top_10_bowlers.iterrows():
        pid = r['player_id']
        p_deliv = df_deliv[(df_deliv['bowler_id'] == pid) & (df_deliv['is_pressure_ball'] == True)]
        
        # Identify match with most pressure dots / wickets
        m_perf = p_deliv.groupby(['match_id', 'match_date', 'format']).agg(
            pressure_dots=('bowler_runs_conceded', lambda s: (s == 0).sum()),
            pressure_wkts=('is_bowler_wicket', 'sum'),
            pressure_balls=('is_legal', 'sum')
        ).reset_index().sort_values(['pressure_wkts', 'pressure_dots'], ascending=False)
        
        best_m = m_perf.iloc[0] if len(m_perf) > 0 else None
        sig_str = f"Match {int(best_m['match_id'])} ({best_m['format']}, {best_m['match_date']}): {int(best_m['pressure_wkts'])} wkts, {int(best_m['pressure_dots'])} dots in {int(best_m['pressure_balls'])} pressure balls" if best_m is not None else "N/A"
        
        cci, cri, dei = r['CCI'], r['CRI'], r['DEI']
        if dei == max(cci, cri, dei):
            archetype = "Death Yorker / Choke Specialist"
        elif cci == max(cci, cri, dei):
            archetype = "Chase Defender / Squeeze Specialist"
        else:
            archetype = "Breakthrough Wicket Taker"
            
        bw_dossiers.append({
            "player_id": pid,
            "player_name": r['player_name'],
            "role": "Bowler",
            "pressure_rank": r['pressure_rank'],
            "pressure_archetype": archetype,
            "CPRI_score": r['CPRI'],
            "CPRI_95_CI": f"[{r['CPRI_lower95']:.2f}, {r['CPRI_upper95']:.2f}]",
            "normal_econ": r['normal_econ'],
            "pressure_econ": r['pressure_econ'],
            "delta_econ": r['delta_econ'],
            "CCI": r['CCI'],
            "CRI": r['CRI'],
            "DEI": r['DEI'],
            "pressure_deliveries": int(r['pressure_legal_balls']),
            "signature_match_evidence": sig_str,
            "auction_tier": "Tier 1 - Marquee Clutch Asset" if r['pressure_rank'] <= 5 else "Tier 2 - Premium Situational Asset"
        })

    df_dossiers = pd.concat([pd.DataFrame(bat_dossiers), pd.DataFrame(bw_dossiers)], ignore_index=True)
    dossiers_path = os.path.join(TABLES_DIR, "player_dossiers.csv")
    df_dossiers.to_csv(dossiers_path, index=False)
    print(f"  Saved forensic player dossiers to: {dossiers_path}")

    # -------------------------------------------------------------
    # 4. GENERATING TOP 10 VISUALIZATIONS
    # -------------------------------------------------------------
    print("\n[Step 4/6] Generating Top 10 Visualizations...")
    
    # Chart 1: Top 10 Batters
    fig, ax = plt.subplots(figsize=(12, 7))
    y_pos = np.arange(len(top_10_batters))
    scores = top_10_batters['CPRI']
    errors = top_10_batters['cpri_se'] * 1.96
    
    bars = ax.barh(y_pos, scores, xerr=errors, align='center', color='#1f77b4', alpha=0.85, capsize=5, ecolor='black')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(top_10_batters['player_name'], fontsize=11, fontweight='bold')
    ax.invert_yaxis()
    ax.set_xlabel("Composite Pressure Reliability Index (CPRI) ± 95% CI", fontsize=11, fontweight='bold')
    ax.set_title("RR Pressure Index 2027 — Top 10 Most Reliable Batters Under Pressure", fontsize=13, fontweight='bold')
    
    # Annotate with Delta SR and CPRI
    for i, bar in enumerate(bars):
        score_val = scores.iloc[i]
        delta_val = top_10_batters['delta_sr'].iloc[i]
        n_val = int(top_10_batters['pressure_balls'].iloc[i])
        ax.text(score_val + errors.iloc[i] + 1.2, bar.get_y() + bar.get_height()/2, 
                f"CPRI: {score_val:.1f} (ΔSR: {delta_val:+.1f}, N={n_val})", 
                va='center', fontsize=9.5, fontweight='bold', color='#111111')

    ax.set_xlim(50, 110)
    plt.tight_layout()
    chart_bat_path = os.path.join(CHARTS_DIR, "top_10_batters_pressure.png")
    plt.savefig(chart_bat_path, dpi=300)
    plt.close()
    print(f"  Saved Top 10 Batters chart to: {chart_bat_path}")

    # Chart 2: Top 10 Bowlers
    fig, ax = plt.subplots(figsize=(12, 7))
    y_pos = np.arange(len(top_10_bowlers))
    scores = top_10_bowlers['CPRI']
    errors = top_10_bowlers['cpri_se'] * 1.96
    
    bars = ax.barh(y_pos, scores, xerr=errors, align='center', color='#d62728', alpha=0.85, capsize=5, ecolor='black')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(top_10_bowlers['player_name'], fontsize=11, fontweight='bold')
    ax.invert_yaxis()
    ax.set_xlabel("Composite Pressure Reliability Index (CPRI) ± 95% CI", fontsize=11, fontweight='bold')
    ax.set_title("RR Pressure Index 2027 — Top 10 Most Reliable Bowlers Under Pressure", fontsize=13, fontweight='bold')
    
    for i, bar in enumerate(bars):
        score_val = scores.iloc[i]
        delta_val = top_10_bowlers['delta_econ'].iloc[i]
        n_val = int(top_10_bowlers['pressure_legal_balls'].iloc[i])
        ax.text(score_val + errors.iloc[i] + 1.2, bar.get_y() + bar.get_height()/2, 
                f"CPRI: {score_val:.1f} (ΔEcon: {delta_val:+.2f}, N={n_val})", 
                va='center', fontsize=9.5, fontweight='bold', color='#111111')

    ax.set_xlim(50, 100)
    plt.tight_layout()
    chart_bw_path = os.path.join(CHARTS_DIR, "top_10_bowlers_pressure.png")
    plt.savefig(chart_bw_path, dpi=300)
    plt.close()
    print(f"  Saved Top 10 Bowlers chart to: {chart_bw_path}")

    # Chart 3: Contextual Profile Comparison (Top Batters vs Bowlers)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("RR Pressure Index 2027 — Contextual Index Profiles (CCI, CRI, DEI)", fontsize=13, fontweight='bold')
    
    # Batters Parallel Comparison
    top_5_bat = top_10_batters.head(5)[['player_name', 'CCI', 'CRI', 'DEI']].set_index('player_name')
    top_5_bat.T.plot(ax=axes[0], marker='o', linewidth=2.5)
    axes[0].set_title("Top 5 Batters: Dimensional Profile Comparison")
    axes[0].set_ylabel("Index Score (Mean=50, Std=15)")
    axes[0].set_ylim(40, 115)
    axes[0].grid(True, linestyle='--', alpha=0.5)

    # Bowlers Parallel Comparison
    top_5_bw = top_10_bowlers.head(5)[['player_name', 'CCI', 'CRI', 'DEI']].set_index('player_name')
    top_5_bw.T.plot(ax=axes[1], marker='s', linewidth=2.5)
    axes[1].set_title("Top 5 Bowlers: Dimensional Profile Comparison")
    axes[1].set_ylabel("Index Score (Mean=50, Std=15)")
    axes[1].set_ylim(40, 115)
    axes[1].grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    chart_radar_path = os.path.join(CHARTS_DIR, "radar_context_profiles.png")
    plt.savefig(chart_radar_path, dpi=300)
    plt.close()
    print(f"  Saved Contextual Profiles chart to: {chart_radar_path}")

    # -------------------------------------------------------------
    # 5. POWER BI STAR SCHEMA DATA MODEL EXPORT
    # -------------------------------------------------------------
    print("\n[Step 5/6] Exporting Power BI Star Schema Dimension and Fact Tables...")
    # Dim Players
    dim_players = df_summary[['player_id', 'player_name', 'role_type', 'overall_balls', 'pressure_balls', 'ipl_balls', 't20i_balls']].drop_duplicates().copy()
    dim_players_path = os.path.join(DASHBOARD_DIR, "dim_players.csv")
    dim_players.to_csv(dim_players_path, index=False)
    
    # Fact Player Rankings
    fact_rankings_path = os.path.join(DASHBOARD_DIR, "fact_player_rankings.csv")
    full_rankings.to_csv(fact_rankings_path, index=False)
    
    # Fact Player Dossiers
    fact_dossiers_path = os.path.join(DASHBOARD_DIR, "fact_player_dossiers.csv")
    df_dossiers.to_csv(fact_dossiers_path, index=False)
    
    print(f"  Exported Power BI tables to: {DASHBOARD_DIR}")

    # -------------------------------------------------------------
    # 6. PRINT EXECUTIVE SUMMARY TABLE
    # -------------------------------------------------------------
    print("\n" + "=" * 80)
    print("OFFICIAL TOP 10 BATTERS UNDER PRESSURE:")
    print(top_10_batters[['pressure_rank', 'player_name', 'pressure_balls', 'normal_sr', 'pressure_sr', 'delta_sr', 'CCI', 'CRI', 'DEI', 'CPRI']].to_string(index=False))

    print("\nOFFICIAL TOP 10 BOWLERS UNDER PRESSURE:")
    print(top_10_bowlers[['pressure_rank', 'player_name', 'pressure_legal_balls', 'normal_econ', 'pressure_econ', 'delta_econ', 'CCI', 'CRI', 'DEI', 'CPRI']].to_string(index=False))
    print("=" * 80)

if __name__ == "__main__":
    run_ranking_engine()

