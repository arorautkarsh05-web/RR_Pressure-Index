"""
RR PRESSURE INDEX 2027 — COMPILE DATA FOR INTERACTIVE HTML DASHBOARD
Phase 04: Production Visualization

This script extracts and bundles all certified analytical data into:
dashboard/html/data/dashboard_data.json
Ensures the HTML dashboard runs completely offline without any backend or external API calls.
"""

import os
import sys
import json
import pandas as pd
import numpy as np

PROJECT_ROOT = r"d:\RR_PRESSURE_INDEX_2027"
DASHBOARD_DATA_DIR = os.path.join(PROJECT_ROOT, "outputs", "dashboard")
AUDIT_DIR = os.path.join(PROJECT_ROOT, "outputs", "audit")
RANKINGS_DIR = os.path.join(PROJECT_ROOT, "outputs", "rankings")
TABLES_DIR = os.path.join(PROJECT_ROOT, "outputs", "tables")
HTML_DATA_DIR = os.path.join(PROJECT_ROOT, "dashboard", "html", "data")

os.makedirs(HTML_DATA_DIR, exist_ok=True)

def compile_html_data():
    print("=" * 80)
    print("COMPILING CERTIFIED DASHBOARD JSON DATA BUNDLE")
    print("=" * 80)
    
    # 1. Macro KPIs
    kpis = {
        "senior_matches": 837,
        "total_deliveries": 194014,
        "batting_legal_deliveries": 186540,
        "bowling_legal_deliveries": 185715,
        "unique_players": 891,
        "total_baseline_profiles": 1235,
        "qualified_batters": 117,
        "qualified_bowlers": 250,
        "batting_pressure_deliveries": 24016,
        "bowling_leverage_deliveries": 41202,
        "ipl_matches": 367,
        "t20i_matches": 470,
        "top_batting_cpri": 74.41,
        "top_batter_name": "Naman Dhir",
        "top_bowling_cpri": 76.83,
        "top_bowler_name": "Jasprit Bumrah"
    }
    
    # 2. Rankings & Full Profiles
    top_bat = pd.read_csv(os.path.join(RANKINGS_DIR, "top_10_batters.csv"))
    top_bowl = pd.read_csv(os.path.join(RANKINGS_DIR, "top_10_bowlers.csv"))
    
    dim_ranking = pd.read_csv(os.path.join(DASHBOARD_DATA_DIR, "dim_ranking.csv"))
    fact_pressure = pd.read_csv(os.path.join(DASHBOARD_DATA_DIR, "fact_player_pressure_performance.csv"))
    dim_player = pd.read_csv(os.path.join(DASHBOARD_DATA_DIR, "dim_player.csv"))
    auc_ev = pd.read_csv(os.path.join(AUDIT_DIR, "auction_transferability_validation.csv"))
    jack_df = pd.read_csv(os.path.join(AUDIT_DIR, "jackknife_full_results.csv"))
    post_df = pd.read_csv(os.path.join(AUDIT_DIR, "posterior_interpretation_audit.csv"))
    match_rec = pd.read_csv(os.path.join(AUDIT_DIR, "player_match_reconciliation.csv"))
    
    # Merge rich details for Top 10 Batters
    batters_list = []
    for idx, row in top_bat.iterrows():
        pid = int(row['player_id'])
        pname = row['player_name']
        
        ev_row = auc_ev[(auc_ev['Player_Name'] == pname) & (auc_ev['Discipline'] == 'Batter')].iloc[0]
        post_row = post_df[(post_df['player_id'] == pid) & (post_df['discipline'] == 'Batter')].iloc[0]
        jack_row = jack_df[(jack_df['player_id'] == pid) & (jack_df['discipline'] == 'Batter')].iloc[0]
        m_row = match_rec[(match_rec['player_id'] == pid) & (match_rec['discipline'] == 'Batter')].iloc[0]
        
        batters_list.append({
            "rank": int(row['pressure_rank']),
            "player_id": pid,
            "player_name": pname,
            "discipline": "Batter",
            "cpri": float(row['CPRI']),
            "cpri_ci_low": float(row['cpri_ci_low']),
            "cpri_ci_high": float(row['cpri_ci_high']),
            "pressure_balls": int(row['pressure_balls']),
            "pressure_sr": float(row['press_performance_sr']),
            "normal_sr": float(row['norm_baseline_sr']),
            "delta_sr": float(row['delta_context_sr']),
            "bayes_sr": float(row['bayes_estimate_sr']),
            "bayes_ci_low": float(row['ci_95_low']),
            "bayes_ci_high": float(row['ci_95_high']),
            "ci_width": float(row['ci_95_width']),
            "match_cv": float(row['consistency_cv']),
            "match_success_rate": float(row['match_success_rate'] * 100.0),
            "confidence_tier": row['confidence_class'],
            "ranking_explanation": row['ranking_explanation'],
            "ipl_balls": int(ev_row['IPL_Pressure_Balls']),
            "t20i_balls": int(ev_row['T20I_Pressure_Balls']),
            "dim1_ipl_grade": ev_row['Dim1_IPL_Evidence_Grade'],
            "dim4_venue_grade": ev_row['Dim4_Venue_Transferability_Grade'],
            "dim5_role": ev_row['Dim5_Tactical_Role_Specialization'],
            "overall_evidence_tier": ev_row['Overall_Auction_Evidence_Tier'],
            "p_rank_1": float(post_row['p_rank_1_pct']),
            "p_top_5": float(post_row['p_rank_le_5_pct']),
            "p_top_10": float(post_row['p_rank_le_10_pct']),
            "median_rank": float(post_row['median_posterior_rank']),
            "jackknife_worst_case": float(jack_row['worst_case_metric_lomo']),
            "jackknife_se": float(jack_row['jackknife_se']),
            "max_rank_drop": int(jack_row['max_rank_degradation']),
            "jackknife_verdict": jack_row['jackknife_verdict'],
            "qualified_matches": int(m_row['qualified_pressure_matches_ge3']),
            "total_xi_matches": int(m_row['total_playing_xi_matches'])
        })
        
    # Merge rich details for Top 10 Bowlers
    bowlers_list = []
    for idx, row in top_bowl.iterrows():
        pid = int(row['player_id'])
        pname = row['player_name']
        
        ev_row = auc_ev[(auc_ev['Player_Name'] == pname) & (auc_ev['Discipline'] == 'Bowler')].iloc[0]
        post_row = post_df[(post_df['player_id'] == pid) & (post_df['discipline'] == 'Bowler')].iloc[0]
        jack_row = jack_df[(jack_df['player_id'] == pid) & (jack_df['discipline'] == 'Bowler')].iloc[0]
        m_row = match_rec[(match_rec['player_id'] == pid) & (match_rec['discipline'] == 'Bowler')].iloc[0]
        
        bowlers_list.append({
            "rank": int(row['pressure_rank']),
            "player_id": pid,
            "player_name": pname,
            "discipline": "Bowler",
            "cpri": float(row['CPRI']),
            "cpri_ci_low": float(row['cpri_ci_low']),
            "cpri_ci_high": float(row['cpri_ci_high']),
            "pressure_balls": int(row['pressure_balls']),
            "leverage_econ": float(row['press_performance_econ']),
            "normal_econ": float(row['norm_baseline_econ']),
            "delta_econ": float(row['delta_context_econ']),
            "bayes_econ": float(row['bayes_estimate_econ']),
            "bayes_ci_low": float(row['ci_95_low']),
            "bayes_ci_high": float(row['ci_95_high']),
            "ci_width": float(row['ci_95_width']),
            "match_cv": float(row['consistency_cv']),
            "match_success_rate": float(row['match_success_rate'] * 100.0),
            "confidence_tier": row['confidence_class'],
            "ranking_explanation": row['ranking_explanation'],
            "ipl_balls": int(ev_row['IPL_Pressure_Balls']),
            "t20i_balls": int(ev_row['T20I_Pressure_Balls']),
            "dim1_ipl_grade": ev_row['Dim1_IPL_Evidence_Grade'],
            "dim4_venue_grade": ev_row['Dim4_Venue_Transferability_Grade'],
            "dim5_role": ev_row['Dim5_Tactical_Role_Specialization'],
            "overall_evidence_tier": ev_row['Overall_Auction_Evidence_Tier'],
            "p_rank_1": float(post_row['p_rank_1_pct']),
            "p_top_5": float(post_row['p_rank_le_5_pct']),
            "p_top_10": float(post_row['p_rank_le_10_pct']),
            "median_rank": float(post_row['median_posterior_rank']),
            "jackknife_worst_case": float(jack_row['worst_case_metric_lomo']),
            "jackknife_se": float(jack_row['jackknife_se']),
            "max_rank_drop": int(jack_row['max_rank_degradation']),
            "jackknife_verdict": jack_row['jackknife_verdict'],
            "qualified_matches": int(m_row['qualified_pressure_matches_ge3']),
            "total_xi_matches": int(m_row['total_playing_xi_matches'])
        })
        
    # 3. Full Qualified Cohort (All qualified batters N>=50 and bowlers N>=60)
    p_names = dict(zip(dim_player['PlayerID'], dim_player['PlayerName']))
    
    cohort_batters = []
    bat_p_sub = fact_pressure[(fact_pressure['Discipline'] == 'Batter') & (fact_pressure['PressureBalls'] >= 50)].copy()
    for idx, row in bat_p_sub.iterrows():
        cohort_batters.append({
            "player_id": int(row['PlayerID']),
            "player_name": p_names.get(int(row['PlayerID']), f"Player {row['PlayerID']}"),
            "pressure_balls": int(row['PressureBalls']),
            "normal_balls": int(row['NormalBalls']),
            "pressure_sr": float(row['RawPressureMetric']),
            "normal_sr": float(row['NormalBaselineMetric']),
            "delta_sr": float(row['DeltaContextMetric']),
            "bayes_sr": float(row['BayesEstimate']),
            "bayes_ci_low": float(row['Bayes_CI_Low']),
            "bayes_ci_high": float(row['Bayes_CI_High']),
            "boundary_pct": float(row['BoundaryPct']),
            "dot_pct": float(row['DotPct']),
            "match_cv": float(row['MatchCV']) if not pd.isna(row['MatchCV']) else None,
            "match_success_rate": float(row['MatchSuccessRate']) if not pd.isna(row['MatchSuccessRate']) else None
        })
        
    cohort_bowlers = []
    bowl_p_sub = fact_pressure[(fact_pressure['Discipline'] == 'Bowler') & (fact_pressure['PressureBalls'] >= 60)].copy()
    for idx, row in bowl_p_sub.iterrows():
        cohort_bowlers.append({
            "player_id": int(row['PlayerID']),
            "player_name": p_names.get(int(row['PlayerID']), f"Player {row['PlayerID']}"),
            "leverage_balls": int(row['PressureBalls']),
            "normal_balls": int(row['NormalBalls']),
            "leverage_econ": float(row['RawPressureMetric']),
            "normal_econ": float(row['NormalBaselineMetric']),
            "delta_econ": float(row['DeltaContextMetric']),
            "bayes_econ": float(row['BayesEstimate']),
            "bayes_ci_low": float(row['Bayes_CI_Low']),
            "bayes_ci_high": float(row['Bayes_CI_High']),
            "conceded_boundary_pct": float(row['BoundaryPct']),
            "dot_pct": float(row['DotPct']),
            "wicket_rate": float(row['DismissalOrWktRate']),
            "match_cv": float(row['MatchCV']) if not pd.isna(row['MatchCV']) else None,
            "match_success_rate": float(row['MatchSuccessRate']) if not pd.isna(row['MatchSuccessRate']) else None
        })

    # 4. Situational Splits for Top Players
    # Load situational splits from dashboard/data/Fact_Situation_Splits.csv if exists
    splits_path = os.path.join(PROJECT_ROOT, "dashboard", "data", "Fact_Situation_Splits.csv")
    situational_splits = []
    if os.path.exists(splits_path):
        splits_df = pd.read_csv(splits_path)
        for idx, row in splits_df.iterrows():
            situational_splits.append({
                "player_id": int(row['PlayerID']),
                "player_name": p_names.get(int(row['PlayerID']), f"Player {row['PlayerID']}"),
                "discipline": row['Discipline'],
                "situation": row['Situation'],
                "balls": int(row['Balls']),
                "runs": int(row['Runs']),
                "rate": float(row['RateMetric']),
                "boundary_pct": float(row['BoundaryPct']),
                "dot_pct": float(row['DotPct'])
            })

    # Assemble Bundle
    bundle = {
        "kpis": kpis,
        "top_10_batters": batters_list,
        "top_10_bowlers": bowlers_list,
        "cohort_batters": cohort_batters,
        "cohort_bowlers": cohort_bowlers,
        "situational_splits": situational_splits
    }
    
    out_json = os.path.join(HTML_DATA_DIR, "dashboard_data.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=2)
        
    print(f"[SUCCESS] Exported offline dashboard bundle to: {out_json}")
    print(f"  Bundle Size: {os.path.getsize(out_json):,} bytes")
    print(f"  Top Batters: {len(batters_list)}, Top Bowlers: {len(bowlers_list)}")
    print(f"  Cohort Batters: {len(cohort_batters)}, Cohort Bowlers: {len(cohort_bowlers)}")
    return bundle

if __name__ == "__main__":
    compile_html_data()

