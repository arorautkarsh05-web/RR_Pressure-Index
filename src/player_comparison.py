"""
RR PRESSURE INDEX 2027 — PHASE 03: PLAYER COMPARISON ENGINE & VISUAL ANALYTICS
Generates Head-to-Head Comparative Analyses and 4 Publication-Grade Visualizations.

Charts Generated:
1. outputs/charts/top_batters_comparison.png
2. outputs/charts/top_bowlers_comparison.png
3. outputs/charts/player_consistency.png
4. outputs/charts/pressure_vs_baseline.png
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
os.makedirs(CHARTS_DIR, exist_ok=True)

# Rajasthan Royals Aesthetic Palette
RR_PINK = "#D41B66"
RR_DARK_BLUE = "#1B2A47"
ACCENT_BLUE = "#0072CE"
GOLD = "#E5A93C"
GREEN = "#2A9D8F"
GRAY_TEXT = "#4A4E69"

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    'axes.edgecolor': '#D3D3D3',
    'axes.linewidth': 0.8,
    'grid.color': '#EBEBEB',
    'grid.linestyle': '--',
    'grid.alpha': 0.7,
})

def run_player_comparison():
    print("=" * 80)
    print("RR PRESSURE INDEX 2027 — PLAYER COMPARISON & VISUAL ANALYTICS")
    print("=" * 80)

    # 1. Load Ranked Datasets
    print("\n[Step 1/5] Loading official Top 10 rankings and performance profiles...")
    top_bat = pd.read_csv(os.path.join(RANKINGS_DIR, "top_10_batters.csv"))
    top_bw = pd.read_csv(os.path.join(RANKINGS_DIR, "top_10_bowlers.csv"))
    all_bat = pd.read_csv(os.path.join(TABLES_DIR, "batter_performance_profiles.csv"))
    all_bw = pd.read_csv(os.path.join(TABLES_DIR, "bowler_performance_profiles.csv"))

    # -------------------------------------------------------------
    # 2. CHART 1: TOP 10 BATTERS COMPARISON
    # -------------------------------------------------------------
    print("\n[Step 2/5] Generating Chart 1: Top 10 Batters Forest Comparison...")
    fig, ax = plt.subplots(figsize=(14, 7), dpi=300)

    top_bat_rev = top_bat.iloc[::-1].reset_index(drop=True)
    y_pos = np.arange(len(top_bat_rev))

    # Error bar for Bayesian 95% Credible Interval
    ax.errorbar(top_bat_rev['bayes_estimate_sr'], y_pos,
                xerr=[top_bat_rev['bayes_estimate_sr'] - top_bat_rev['ci_95_low'],
                      top_bat_rev['ci_95_high'] - top_bat_rev['bayes_estimate_sr']],
                fmt='o', color=RR_PINK, ecolor=RR_DARK_BLUE, elinewidth=2.0, capsize=4.5,
                markersize=8, label='Bayesian Posterior Pressure SR (95% CI)', zorder=5)

    # Normal Baseline and Raw Pressure
    ax.scatter(top_bat_rev['norm_baseline_sr'], y_pos, color='gray', marker='s', s=45, label='Normal Career Baseline SR', zorder=4)
    ax.scatter(top_bat_rev['press_performance_sr'], y_pos, color=GOLD, marker='^', s=55, label='Raw Empirical Pressure SR', zorder=4)

    # Annotate CPRI and Confidence
    for idx, row in top_bat_rev.iterrows():
        tier_tag = "Tier A" if "Tier A" in row['confidence_class'] else "Tier B"
        ax.annotate(f"CPRI: {row['CPRI']:.1f} ({tier_tag}, N={int(row['pressure_balls'])})",
                    xy=(max(row['ci_95_high'], row['press_performance_sr']) + 3.0, idx),
                    va='center', fontsize=8.5, fontweight='bold', color=RR_DARK_BLUE)

    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"#{r['pressure_rank']} {r['player_name']} ({r['competitions']})" for _, r in top_bat_rev.iterrows()], fontsize=10, fontweight='bold')
    ax.axvline(147.4, color='gray', linestyle=':', label='Population Prior Mean (147.4)')
    ax.set_title("TOP 10 BATTERS UNDER PRESSURE — BAYESIAN ESTIMATES & 95% CREDIBLE INTERVALS", fontsize=12, fontweight='bold', pad=12)
    ax.set_xlabel("Strike Rate under Pressure (Balls Faced)", fontsize=11)
    ax.set_xlim(110, 290)
    ax.legend(loc='lower left', frameon=True, facecolor='white', framealpha=0.9, fontsize=9)
    ax.grid(True, axis='x')

    plt.tight_layout()
    chart1_path = os.path.join(CHARTS_DIR, "top_batters_comparison.png")
    fig.savefig(chart1_path)
    plt.close(fig)
    print(f"  Saved Chart 1 to: {chart1_path}")

    # -------------------------------------------------------------
    # 3. CHART 2: TOP 10 BOWLERS COMPARISON
    # -------------------------------------------------------------
    print("\n[Step 3/5] Generating Chart 2: Top 10 Bowlers Forest Comparison...")
    fig, ax = plt.subplots(figsize=(14, 7), dpi=300)

    top_bw_rev = top_bw.iloc[::-1].reset_index(drop=True)
    y_pos = np.arange(len(top_bw_rev))

    # Error bar for Bayesian 95% Credible Interval
    ax.errorbar(top_bw_rev['bayes_estimate_econ'], y_pos,
                xerr=[top_bw_rev['bayes_estimate_econ'] - top_bw_rev['ci_95_low'],
                      top_bw_rev['ci_95_high'] - top_bw_rev['bayes_estimate_econ']],
                fmt='o', color=ACCENT_BLUE, ecolor=RR_DARK_BLUE, elinewidth=2.0, capsize=4.5,
                markersize=8, label='Bayesian Posterior Leverage Economy (95% CI)', zorder=5)

    # Normal Baseline and Raw Leverage
    ax.scatter(top_bw_rev['norm_baseline_econ'], y_pos, color='gray', marker='s', s=45, label='Normal Career Baseline Economy', zorder=4)
    ax.scatter(top_bw_rev['press_performance_econ'], y_pos, color=GOLD, marker='^', s=55, label='Raw Empirical Leverage Economy', zorder=4)

    # Annotate CPRI and Confidence
    for idx, row in top_bw_rev.iterrows():
        tier_tag = "Tier A" if "Tier A" in row['confidence_class'] else "Tier B"
        ax.annotate(f"CPRI: {row['CPRI']:.1f} ({tier_tag}, N={int(row['pressure_balls'])})",
                    xy=(min(row['ci_95_low'], row['press_performance_econ']) - 0.2, idx),
                    ha='right', va='center', fontsize=8.5, fontweight='bold', color=RR_DARK_BLUE)

    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"#{r['pressure_rank']} {r['player_name']} ({r['competitions']})" for _, r in top_bw_rev.iterrows()], fontsize=10, fontweight='bold')
    ax.axvline(9.12, color='gray', linestyle=':', label='Population Prior Mean Economy (9.12)')
    ax.set_title("TOP 10 BOWLERS UNDER LEVERAGE — BAYESIAN ESTIMATES & 95% CREDIBLE INTERVALS", fontsize=12, fontweight='bold', pad=12)
    ax.set_xlabel("Economy Rate under Pressure (Runs Per Over — Lower is Superior)", fontsize=11)
    ax.set_xlim(2.5, 11.5)
    ax.legend(loc='lower right', frameon=True, facecolor='white', framealpha=0.9, fontsize=9)
    ax.grid(True, axis='x')

    plt.tight_layout()
    chart2_path = os.path.join(CHARTS_DIR, "top_bowlers_comparison.png")
    fig.savefig(chart2_path)
    plt.close(fig)
    print(f"  Saved Chart 2 to: {chart2_path}")

    # -------------------------------------------------------------
    # 4. CHART 3: PLAYER CONSISTENCY SCATTER
    # -------------------------------------------------------------
    print("\n[Step 4/5] Generating Chart 3: Match-Level Consistency Analytics...")
    fig, axes = plt.subplots(1, 2, figsize=(15, 6), dpi=300)

    # Batters Consistency: CV vs Success Rate
    ax = axes[0]
    q_bat = all_bat[all_bat['pressure_balls'] >= 40].dropna(subset=['match_sr_cv', 'match_success_rate_140']).copy()
    top_pids_bat = set(top_bat['player_id'])
    
    ax.scatter(q_bat.loc[~q_bat['player_id'].isin(top_pids_bat), 'match_sr_cv'],
               q_bat.loc[~q_bat['player_id'].isin(top_pids_bat), 'match_success_rate_140'] * 100,
               color='#CCCCCC', alpha=0.6, s=30, label='Other Qualified Batters')

    top_bat_pts = q_bat[q_bat['player_id'].isin(top_pids_bat)]
    ax.scatter(top_bat_pts['match_sr_cv'], top_bat_pts['match_success_rate_140'] * 100,
               color=RR_PINK, s=70, edgecolors=RR_DARK_BLUE, linewidth=1.2, label='Top 10 Batters', zorder=5)

    for _, r in top_bat_pts.iterrows():
        ax.annotate(r['player_name'].split()[-1], xy=(r['match_sr_cv'], r['match_success_rate_140'] * 100),
                    xytext=(4, 2), textcoords='offset points', fontsize=8.5, fontweight='bold', color=RR_DARK_BLUE)

    ax.axhline(50, color='gray', linestyle='--', linewidth=0.8)
    ax.set_title("Batting Consistency: Volatility (CV) vs. High-Strike Match Rate", fontsize=11, fontweight='bold', pad=10)
    ax.set_xlabel("Match-Level SR Coefficient of Variation (CV — Lower is More Consistent)", fontsize=10)
    ax.set_ylabel("% of Matches with Pressure SR >= 140", fontsize=10)
    ax.legend(loc='lower left', frameon=True, facecolor='white', framealpha=0.9, fontsize=8.5)
    ax.grid(True)

    # Bowlers Consistency: CV vs Sub-8.50 rpo rate
    ax2 = axes[1]
    q_bw = all_bw[all_bw['pressure_balls'] >= 50].dropna(subset=['match_econ_cv', 'match_success_rate_sub85']).copy()
    top_pids_bw = set(top_bw['player_id'])

    ax2.scatter(q_bw.loc[~q_bw['player_id'].isin(top_pids_bw), 'match_econ_cv'],
                q_bw.loc[~q_bw['player_id'].isin(top_pids_bw), 'match_success_rate_sub85'] * 100,
                color='#CCCCCC', alpha=0.6, s=30, label='Other Qualified Bowlers')

    top_bw_pts = q_bw[q_bw['player_id'].isin(top_pids_bw)]
    ax2.scatter(top_bw_pts['match_econ_cv'], top_bw_pts['match_success_rate_sub85'] * 100,
                color=ACCENT_BLUE, s=70, edgecolors=RR_DARK_BLUE, linewidth=1.2, label='Top 10 Bowlers', zorder=5)

    for _, r in top_bw_pts.iterrows():
        ax2.annotate(r['player_name'].split()[-1], xy=(r['match_econ_cv'], r['match_success_rate_sub85'] * 100),
                     xytext=(4, 2), textcoords='offset points', fontsize=8.5, fontweight='bold', color=RR_DARK_BLUE)

    ax2.axhline(60, color='gray', linestyle='--', linewidth=0.8)
    ax2.set_title("Bowling Consistency: Volatility (CV) vs. Sub-8.50 Economy Match Rate", fontsize=11, fontweight='bold', pad=10)
    ax2.set_xlabel("Match-Level Economy CV (Lower is More Consistent)", fontsize=10)
    ax2.set_ylabel("% of Matches with Leverage Economy <= 8.50 rpo", fontsize=10)
    ax2.legend(loc='lower left', frameon=True, facecolor='white', framealpha=0.9, fontsize=8.5)
    ax2.grid(True)

    plt.tight_layout()
    chart3_path = os.path.join(CHARTS_DIR, "player_consistency.png")
    fig.savefig(chart3_path)
    plt.close(fig)
    print(f"  Saved Chart 3 to: {chart3_path}")

    # -------------------------------------------------------------
    # 5. CHART 4: PRESSURE VS BASELINE FOUR-QUADRANT PLOT
    # -------------------------------------------------------------
    print("\n[Step 5/5] Generating Chart 4: Four-Quadrant Pressure vs Baseline...")
    fig, axes = plt.subplots(1, 2, figsize=(15, 6), dpi=300)

    # Left: Batting Normal SR vs Delta Context SR
    ax = axes[0]
    q_bat_all = all_bat[all_bat['pressure_balls'] >= 40].copy()
    ax.scatter(q_bat_all['norm_sr'], q_bat_all['delta_context_sr'], color='#B0BEC5', alpha=0.5, s=28)
    
    top_bat_match = q_bat_all[q_bat_all['player_id'].isin(top_pids_bat)]
    ax.scatter(top_bat_match['norm_sr'], top_bat_match['delta_context_sr'], color=RR_PINK, s=75, edgecolors=RR_DARK_BLUE, linewidth=1.2, label='Top 10 Batters')

    for _, r in top_bat_match.iterrows():
        ax.annotate(r['player_name'].split()[-1], xy=(r['norm_sr'], r['delta_context_sr']),
                    xytext=(3, 3), textcoords='offset points', fontsize=8.5, fontweight='bold', color=RR_DARK_BLUE)

    ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
    ax.axvline(135, color='gray', linewidth=0.8, linestyle=':')
    ax.set_title("Batting: Normal Career Baseline vs. Context Pressure Elevation", fontsize=11, fontweight='bold', pad=10)
    ax.set_xlabel("Normal Baseline Strike Rate", fontsize=10)
    ax.set_ylabel("Context-Adjusted Delta SR ($SR_{press} - E[SR]$)", fontsize=10)
    ax.annotate("CLUTCH ELEVATORS\n(High Baseline, High Elevation)", xy=(155, 60), color=RR_PINK, fontsize=8.5, fontweight='bold', ha='center')
    ax.annotate("PRESSURE SPECIALISTS\n(Modest Baseline, High Elevation)", xy=(120, 60), color=ACCENT_BLUE, fontsize=8.5, fontweight='bold', ha='center')
    ax.legend(loc='lower right', frameon=True, facecolor='white', framealpha=0.9)
    ax.grid(True)

    # Right: Bowling Normal Economy vs Delta Context Economy
    ax2 = axes[1]
    q_bw_all = all_bw[all_bw['pressure_balls'] >= 50].copy()
    ax2.scatter(q_bw_all['norm_econ'], q_bw_all['delta_context_econ'], color='#B0BEC5', alpha=0.5, s=28)

    top_bw_match = q_bw_all[q_bw_all['player_id'].isin(top_pids_bw)]
    ax2.scatter(top_bw_match['norm_econ'], top_bw_match['delta_context_econ'], color=ACCENT_BLUE, s=75, edgecolors=RR_DARK_BLUE, linewidth=1.2, label='Top 10 Bowlers')

    for _, r in top_bw_match.iterrows():
        ax2.annotate(r['player_name'].split()[-1], xy=(r['norm_econ'], r['delta_context_econ']),
                     xytext=(3, 3), textcoords='offset points', fontsize=8.5, fontweight='bold', color=RR_DARK_BLUE)

    ax2.axhline(0, color='black', linewidth=0.8, linestyle='--')
    ax2.axvline(8.1, color='gray', linewidth=0.8, linestyle=':')
    ax2.set_title("Bowling: Normal Career Economy vs. Context Pressure Suppression", fontsize=11, fontweight='bold', pad=10)
    ax2.set_xlabel("Normal Baseline Economy (Lower is Superior)", fontsize=10)
    ax2.set_ylabel("Context-Adjusted Delta Econ ($Econ_{press} - E[Econ]$ — Negative is Superior)", fontsize=10)
    ax2.annotate("ELITE STRANGLERS\n(Sub-8.0 Normal, Negative Delta)", xy=(6.5, -2.5), color=ACCENT_BLUE, fontsize=8.5, fontweight='bold', ha='center')
    ax2.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.9)
    ax2.grid(True)

    plt.tight_layout()
    chart4_path = os.path.join(CHARTS_DIR, "pressure_vs_baseline.png")
    fig.savefig(chart4_path)
    plt.close(fig)
    print(f"  Saved Chart 4 to: {chart4_path}")

    print("=" * 80)

if __name__ == "__main__":
    run_player_comparison()

