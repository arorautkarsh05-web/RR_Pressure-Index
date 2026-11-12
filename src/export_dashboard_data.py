"""
RR PRESSURE INDEX 2027 — PHASE 04: DASHBOARD DATA EXPORTER
Exports optimized Star-Schema datasets and auction intelligence for Power BI
and the interactive executive dashboard.
"""

import os
import json
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES_DIR = os.path.join(BASE_DIR, "outputs", "tables")
RANKINGS_DIR = os.path.join(BASE_DIR, "outputs", "rankings")
DASHBOARD_DATA_DIR = os.path.join(BASE_DIR, "dashboard", "data")
os.makedirs(DASHBOARD_DATA_DIR, exist_ok=True)

def export_dashboard_data():
    print("=" * 80)
    print("RR PRESSURE INDEX 2027 — DASHBOARD DATA EXPORT & STAR SCHEMA BUILDER")
    print("=" * 80)

    # 1. Ingest Data
    print("\n[Step 1/5] Ingesting certified ranking tables and player performance profiles...")
    top_bat = pd.read_csv(os.path.join(RANKINGS_DIR, "top_10_batters.csv"))
    top_bw = pd.read_csv(os.path.join(RANKINGS_DIR, "top_10_bowlers.csv"))
    all_bat = pd.read_csv(os.path.join(TABLES_DIR, "batter_performance_profiles.csv"))
    all_bw = pd.read_csv(os.path.join(TABLES_DIR, "bowler_performance_profiles.csv"))
    
    chase_b = pd.read_csv(os.path.join(RANKINGS_DIR, "chasing_clutch_batters.csv"))
    col_b = pd.read_csv(os.path.join(RANKINGS_DIR, "collapse_recovery_batters.csv"))
    death_b = pd.read_csv(os.path.join(RANKINGS_DIR, "death_finishers.csv"))
    death_bw = pd.read_csv(os.path.join(RANKINGS_DIR, "death_execution_bowlers.csv"))
    pp_bw = pd.read_csv(os.path.join(RANKINGS_DIR, "powerplay_enforcers.csv"))

    # 2. Fact Official Rankings Table
    print("\n[Step 2/5] Building fact_official_rankings.csv...")
    bat_rank = top_bat.copy()
    bat_rank['discipline'] = 'Batter'
    bat_rank['primary_metric_label'] = 'Strike Rate'
    bat_rank['press_performance'] = bat_rank['press_performance_sr']
    bat_rank['norm_baseline'] = bat_rank['norm_baseline_sr']
    bat_rank['delta_context'] = bat_rank['delta_context_sr']
    bat_rank['bayes_estimate'] = bat_rank['bayes_estimate_sr']

    bw_rank = top_bw.copy()
    bw_rank['discipline'] = 'Bowler'
    bw_rank['primary_metric_label'] = 'Economy Rate'
    bw_rank['press_performance'] = bw_rank['press_performance_econ']
    bw_rank['norm_baseline'] = bw_rank['norm_baseline_econ']
    bw_rank['delta_context'] = bw_rank['delta_context_econ']
    bw_rank['bayes_estimate'] = bw_rank['bayes_estimate_econ']

    common_cols = [
        'pressure_rank', 'discipline', 'player_id', 'player_name', 'competitions', 'matches',
        'pressure_balls', 'primary_metric_label', 'press_performance', 'norm_baseline', 'delta_context',
        'bayes_estimate', 'ci_95_low', 'ci_95_high', 'ci_95_width',
        'consistency_cv', 'match_success_rate', 'confidence_class', 'CPRI', 'cpri_ci_low', 'cpri_ci_high', 'ranking_explanation'
    ]
    fact_rankings = pd.concat([bat_rank[common_cols], bw_rank[common_cols]], ignore_index=True)
    fact_rankings_path = os.path.join(DASHBOARD_DATA_DIR, "fact_official_rankings.csv")
    fact_rankings.to_csv(fact_rankings_path, index=False)
    print(f"  Saved {len(fact_rankings)} official ranked records to: {fact_rankings_path}")

    # 3. Fact Specialized Leaderboards Table
    print("\n[Step 3/5] Consolidating fact_specialized_leaderboards.csv...")
    chase_b_clean = chase_b.copy()
    chase_b_clean['category'] = 'Chasing Clutch Batters'
    chase_b_clean['metric_label'] = 'Chase SR'
    chase_b_clean['metric_value'] = chase_b_clean['chase_press_sr']
    chase_b_clean['secondary_metric_label'] = 'Chase Avg'
    chase_b_clean['secondary_metric_value'] = chase_b_clean['chase_press_avg']
    chase_b_clean['balls_count'] = chase_b_clean['chase_press_balls']

    col_b_clean = col_b.copy()
    col_b_clean['category'] = 'Collapse Recovery Batters'
    col_b_clean['metric_label'] = 'Collapse SR'
    col_b_clean['metric_value'] = col_b_clean['collapse_sr']
    col_b_clean['secondary_metric_label'] = 'Collapse Avg'
    col_b_clean['secondary_metric_value'] = col_b_clean['collapse_avg']
    col_b_clean['balls_count'] = col_b_clean['collapse_balls']

    death_b_clean = death_b.copy()
    death_b_clean['category'] = 'Death Finishers'
    death_b_clean['metric_label'] = 'Death SR'
    death_b_clean['metric_value'] = death_b_clean['death_press_sr']
    death_b_clean['secondary_metric_label'] = 'Death Avg'
    death_b_clean['secondary_metric_value'] = death_b_clean['death_press_avg']
    death_b_clean['balls_count'] = death_b_clean['death_press_balls']

    death_bw_clean = death_bw.copy()
    death_bw_clean['category'] = 'Death Execution Bowlers'
    death_bw_clean['metric_label'] = 'Death Economy'
    death_bw_clean['metric_value'] = death_bw_clean['death_lev_econ']
    death_bw_clean['secondary_metric_label'] = 'Death Wickets'
    death_bw_clean['secondary_metric_value'] = death_bw_clean['death_lev_wkts']
    death_bw_clean['balls_count'] = death_bw_clean['death_lev_balls']

    pp_bw_clean = pp_bw.copy()
    pp_bw_clean['category'] = 'Powerplay Enforcers'
    pp_bw_clean['metric_label'] = 'PP Economy'
    pp_bw_clean['metric_value'] = pp_bw_clean['powerplay_lev_econ']
    pp_bw_clean['secondary_metric_label'] = 'PP Wickets'
    pp_bw_clean['secondary_metric_value'] = pp_bw_clean['powerplay_lev_wkts']
    pp_bw_clean['balls_count'] = pp_bw_clean['powerplay_lev_balls']

    spec_cols = ['category', 'rank', 'player_id', 'player_name', 'competitions', 'balls_count', 'metric_label', 'metric_value', 'secondary_metric_label', 'secondary_metric_value']
    fact_spec = pd.concat([
        chase_b_clean[spec_cols],
        col_b_clean[spec_cols],
        death_b_clean[spec_cols],
        death_bw_clean[spec_cols],
        pp_bw_clean[spec_cols]
    ], ignore_index=True)
    fact_spec_path = os.path.join(DASHBOARD_DATA_DIR, "fact_specialized_leaderboards.csv")
    fact_spec.to_csv(fact_spec_path, index=False)
    print(f"  Saved {len(fact_spec)} specialized leaderboard entries to: {fact_spec_path}")

    # 4. Fact Auction Valuations Table
    print("\n[Step 4/5] Computing fact_auction_valuations.csv...")
    # Evaluate auction pricing multipliers and risk discounts across all qualified players
    auction_list = []
    
    # Process Top 25 Batters
    q_bat = all_bat[all_bat['pressure_balls'] >= 45].copy()
    z_s = (q_bat['bayes_delta_context_sr'] - q_bat['bayes_delta_context_sr'].mean()) / q_bat['bayes_delta_context_sr'].std()
    z_b = (q_bat['bayes_press_boundary_pct'] - q_bat['bayes_press_boundary_pct'].mean()) / q_bat['bayes_press_boundary_pct'].std()
    z_d = -(q_bat['bayes_press_dot_pct'] - q_bat['bayes_press_dot_pct'].mean()) / q_bat['bayes_press_dot_pct'].std()
    z_w = -(q_bat['bayes_press_dismissal_pct'] - q_bat['bayes_press_dismissal_pct'].mean()) / q_bat['bayes_press_dismissal_pct'].std()
    q_bat['CPRI'] = np.round(50.0 + 15.0 * (0.40 * z_s + 0.30 * z_b + 0.15 * z_d + 0.15 * z_w), 2)
    
    for idx, r in q_bat.sort_values('CPRI', ascending=False).head(25).iterrows():
        # Risk discount formula
        ci_w = r['bayes_sr_ci_width']
        risk_discount = float(np.clip((ci_w - 40.0) / 60.0 * 0.20, 0.0, 0.20))
        auction_mult = np.round((r['CPRI'] / 50.0) * (1.0 - risk_discount), 3)
        
        # Tier Assignment
        if r['CPRI'] >= 72.0 and risk_discount <= 0.05:
            tier = "Tier 1: Marquee Core"
            price_guide = "14.0 - 20.0 Cr"
            tactical_role = "Pillar Match-Winner"
        elif r['CPRI'] >= 67.0:
            tier = "Tier 2: Premium Executioner"
            price_guide = "9.0 - 13.5 Cr"
            tactical_role = "Designated Finisher / Enforcer"
        elif r['CPRI'] >= 63.0:
            tier = "Tier 3: Tactical Specialist"
            price_guide = "5.0 - 8.5 Cr"
            tactical_role = "Situational Rebuilder"
        else:
            tier = "Tier 4: Undervalued Steal"
            price_guide = "2.0 - 4.5 Cr"
            tactical_role = "High-Upside Depth"

        auction_list.append({
            'discipline': 'Batter',
            'player_id': r['player_id'],
            'player_name': r['player_name'],
            'competitions': r['competitions'],
            'matches_played': r['total_matches_played'],
            'pressure_balls': r['pressure_balls'],
            'CPRI': r['CPRI'],
            'bayes_metric': r['bayes_press_sr'],
            'bayes_ci_low': r['bayes_sr_ci_low'],
            'bayes_ci_high': r['bayes_sr_ci_high'],
            'ci_width': ci_w,
            'risk_discount_pct': np.round(risk_discount * 100.0, 1),
            'auction_multiplier': auction_mult,
            'valuation_tier': tier,
            'estimated_price_bracket': price_guide,
            'tactical_role': tactical_role,
            'rajasthan_royals_fit': 'High Strategic Fit (Death Finishing / Power Surge)' if 'Death' in str(r.get('death_pressure_share', '')) or r['CPRI'] >= 67.0 else 'Squad Depth Option'
        })

    # Process Top 25 Bowlers
    q_bw = all_bw[all_bw['pressure_balls'] >= 50].copy()
    z_e = -(q_bw['bayes_delta_context_econ'] - q_bw['bayes_delta_context_econ'].mean()) / q_bw['bayes_delta_context_econ'].std()
    z_b = -(q_bw['bayes_press_boundary_pct'] - q_bw['bayes_press_boundary_pct'].mean()) / q_bw['bayes_press_boundary_pct'].std()
    z_d = (q_bw['bayes_press_dot_pct'] - q_bw['bayes_press_dot_pct'].mean()) / q_bw['bayes_press_dot_pct'].std()
    z_w = (q_bw['bayes_press_wicket_pct'] - q_bw['bayes_press_wicket_pct'].mean()) / q_bw['bayes_press_wicket_pct'].std()
    q_bw['CPRI'] = np.round(50.0 + 15.0 * (0.40 * z_e + 0.30 * z_b + 0.15 * z_d + 0.15 * z_w), 2)

    for idx, r in q_bw.sort_values('CPRI', ascending=False).head(25).iterrows():
        ci_w = r['bayes_econ_ci_width']
        risk_discount = float(np.clip((ci_w - 1.2) / 2.5 * 0.20, 0.0, 0.20))
        auction_mult = np.round((r['CPRI'] / 50.0) * (1.0 - risk_discount), 3)

        if r['CPRI'] >= 73.0 and risk_discount <= 0.05:
            tier = "Tier 1: Marquee Core"
            price_guide = "14.0 - 22.0 Cr"
            tactical_role = "All-Phase Bowling Leader"
        elif r['CPRI'] >= 68.0:
            tier = "Tier 2: Premium Executioner"
            price_guide = "8.5 - 13.5 Cr"
            tactical_role = "Death / Powerplay Specialist"
        elif r['CPRI'] >= 64.0:
            tier = "Tier 3: Tactical Specialist"
            price_guide = "4.5 - 8.0 Cr"
            tactical_role = "Middle-Overs Strangler"
        else:
            tier = "Tier 4: Undervalued Steal"
            price_guide = "1.5 - 4.0 Cr"
            tactical_role = "Surge Bowling Value"

        auction_list.append({
            'discipline': 'Bowler',
            'player_id': r['player_id'],
            'player_name': r['player_name'],
            'competitions': r['competitions'],
            'matches_played': r['total_matches_played'],
            'pressure_balls': r['pressure_balls'],
            'CPRI': r['CPRI'],
            'bayes_metric': r['bayes_press_econ'],
            'bayes_ci_low': r['bayes_econ_ci_low'],
            'bayes_ci_high': r['bayes_econ_ci_high'],
            'ci_width': ci_w,
            'risk_discount_pct': np.round(risk_discount * 100.0, 1),
            'auction_multiplier': auction_mult,
            'valuation_tier': tier,
            'estimated_price_bracket': price_guide,
            'tactical_role': tactical_role,
            'rajasthan_royals_fit': 'High Strategic Fit (High-Pace Death Execution)' if r['CPRI'] >= 71.0 else 'Tactical Rotation Specialist'
        })

    df_auction = pd.DataFrame(auction_list)
    fact_auction_path = os.path.join(DASHBOARD_DATA_DIR, "fact_auction_valuations.csv")
    df_auction.to_csv(fact_auction_path, index=False)
    print(f"  Saved {len(df_auction)} auction valuations to: {fact_auction_path}")

    # 5. Summary KPIs JSON for Dashboard Header
    print("\n[Step 5/5] Generating summary_kpis.json for Dashboard Header...")
    kpis = {
        "project_name": "RR PRESSURE INDEX 2027",
        "season_scope": "2022–2026",
        "tournaments_evaluated": 139,
        "total_matches": 853,
        "total_deliveries": 194014,
        "batting_legal_balls": 186540,
        "bowling_legal_balls": 185715,
        "batting_pressure_balls": 19908,
        "bowling_leverage_balls": 74164,
        "decoupled_balls": 17836,
        "win_prob_brier_score": 0.1434,
        "win_prob_roc_auc": 0.8798,
        "phase_confounding_gap_sr": 7.84,
        "batting_icc": 0.0221,
        "bowling_icc": 0.0159,
        "top_batter_overall": "Naman Dhir (CPRI: 74.41)",
        "top_bowler_overall": "Jasprit Bumrah (CPRI: 76.83)",
        "top_chasing_clutch_batter": "Phil Salt (SR: 232.73)",
        "top_death_finisher": "Phil Salt (SR: 267.74)",
        "top_death_bowler": "Salman Mirza (Econ: 5.81)",
        "top_powerplay_enforcer": "George Dockrell (Econ: 4.62)"
    }
    kpi_path = os.path.join(DASHBOARD_DATA_DIR, "summary_kpis.json")
    with open(kpi_path, "w", encoding="utf-8") as f:
        json.dump(kpis, f, indent=2)
    print(f"  Saved Summary KPIs JSON to: {kpi_path}")
    print("=" * 80)

if __name__ == "__main__":
    export_dashboard_data()

