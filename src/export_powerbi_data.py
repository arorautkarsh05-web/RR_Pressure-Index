"""
RR PRESSURE INDEX 2027 — POWER BI STAR-SCHEMA DATA EXPORTER
Phase 04: Analytics Dashboard Architecture & Star-Schema Modelling

This script extracts, models, and exports production-ready Star Schema tables for Power BI:
1. Dim_Player: Master player dimension with roles, confidence tiers, and dual-discipline flags.
2. Dim_Match: Master match dimension with date, tournament (IPL vs T20I), format, and stage.
3. Dim_Team: Master team dimension with team names and short codes.
4. Dim_Pressure_Context: Master context classification dimension.
5. Fact_Player_Pressure_Summary: Unified analytical fact table with CPRI, Bayes metrics, consistency, and auction valuation.
6. Fact_Match_Player_Performance: Match-level grain for time-series and Jackknife drill-throughs.
7. Fact_Situation_Splits: Situational splits (Chasing, Collapse, Death, Powerplay, Normal).
"""

import sys
import os
import numpy as np
import pandas as pd

PROJECT_ROOT = r"d:\RR_PRESSURE_INDEX_2027"
TABLES_DIR = os.path.join(PROJECT_ROOT, "outputs", "tables")
RANKINGS_DIR = os.path.join(PROJECT_ROOT, "outputs", "rankings")
AUDIT_DIR = os.path.join(PROJECT_ROOT, "outputs", "audit")
DASHBOARD_DATA_DIR = os.path.join(PROJECT_ROOT, "dashboard", "data")

os.makedirs(DASHBOARD_DATA_DIR, exist_ok=True)

def build_and_export_powerbi_tables():
    print("=" * 80)
    print("RR PRESSURE INDEX 2027 — POWER BI STAR-SCHEMA EXPORTER")
    print("=" * 80)
    
    # ----------------------------------------------------
    # 1. LOAD RAW & INTERMEDIATE TABLES
    # ----------------------------------------------------
    print("\n[Step 1/7] Loading core datasets...")
    matches_raw = pd.read_csv(os.path.join(PROJECT_ROOT, "matches.csv"))
    teams_raw = pd.read_csv(os.path.join(PROJECT_ROOT, "teams.csv"))
    deliv_features = pd.read_csv(os.path.join(TABLES_DIR, "delivery_pressure_features_v2.csv"), usecols=[
        'match_id', 'innings', 'overid', 'striker_id', 'striker_name', 'bowler_id', 'bowler_name',
        'batting_team_id', 'bowling_team_id', 'is_legal', 'runs', 'bowler_runs_conceded',
        'is_four', 'is_six', 'is_wicket', 'is_bowler_wicket', 'is_bat_pressure', 'is_bat_normal',
        'is_bowl_leverage', 'is_bowl_normal', 'is_bat_chasing_clutch', 'is_collapse_crisis', 'is_death_overs'
    ])
    
    bat_profiles = pd.read_csv(os.path.join(TABLES_DIR, "batter_performance_profiles.csv"))
    bowl_profiles = pd.read_csv(os.path.join(TABLES_DIR, "bowler_performance_profiles.csv"))
    
    top_bat = pd.read_csv(os.path.join(RANKINGS_DIR, "top_10_batters.csv"))
    top_bowl = pd.read_csv(os.path.join(RANKINGS_DIR, "top_10_bowlers.csv"))
    
    trans_matrix = pd.read_csv(os.path.join(TABLES_DIR, "player_transferability_matrix.csv"))
    post_probs = pd.read_csv(os.path.join(AUDIT_DIR, "posterior_rank_probabilities.csv"))
    match_cons = pd.read_csv(os.path.join(AUDIT_DIR, "match_consistency_validation.csv"))
    
    # ----------------------------------------------------
    # 2. BUILD DIM_TEAM
    # ----------------------------------------------------
    print("[Step 2/7] Generating Dim_Team...")
    dim_team = teams_raw[['id', 'name', 'code']].copy()
    dim_team.columns = ['TeamID', 'TeamName', 'TeamCode']
    dim_team.drop_duplicates(subset=['TeamID'], inplace=True)
    dim_team.to_csv(os.path.join(DASHBOARD_DATA_DIR, "Dim_Team.csv"), index=False)
    print(f"  Saved Dim_Team: {len(dim_team)} records")
    
    # ----------------------------------------------------
    # 3. BUILD DIM_MATCH
    # ----------------------------------------------------
    print("[Step 3/7] Generating Dim_Match...")
    dim_match = matches_raw[[
        'id', 'date', 'season', 'format', 'stage', 'knock_out',
        'first_bat_team_id', 'second_bat_team_id', 'win_team_id'
    ]].copy()
    dim_match.columns = [
        'MatchID', 'MatchDate', 'Season', 'Format', 'Stage', 'IsKnockOut',
        'FirstBatTeamID', 'SecondBatTeamID', 'WinTeamID'
    ]
    # Identify Tournament (IPL vs T20I)
    # Check if teams are IPL franchises or International teams
    ipl_team_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15] # Standard IPL team IDs in dataset
    dim_match['Tournament'] = dim_match['FirstBatTeamID'].apply(
        lambda tid: 'IPL' if tid in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13] else 'T20I'
    )
    dim_match.drop_duplicates(subset=['MatchID'], inplace=True)
    dim_match.to_csv(os.path.join(DASHBOARD_DATA_DIR, "Dim_Match.csv"), index=False)
    print(f"  Saved Dim_Match: {len(dim_match)} records")
    
    # ----------------------------------------------------
    # 4. BUILD DIM_PLAYER
    # ----------------------------------------------------
    print("[Step 4/7] Generating Dim_Player...")
    # Gather all unique player IDs and names from features
    strikers = deliv_features[['striker_id', 'striker_name']].drop_duplicates()
    strikers.columns = ['PlayerID', 'PlayerName']
    bowlers = deliv_features[['bowler_id', 'bowler_name']].drop_duplicates()
    bowlers.columns = ['PlayerID', 'PlayerName']
    
    all_players = pd.concat([strikers, bowlers]).drop_duplicates(subset=['PlayerID']).reset_index(drop=True)
    
    bat_pids = set(bat_profiles['player_id'].unique())
    bowl_pids = set(bowl_profiles['player_id'].unique())
    dual_pids = bat_pids.intersection(bowl_pids)
    
    roles = []
    is_dual = []
    bat_conf = []
    bowl_conf = []
    
    bat_conf_dict = dict(zip(bat_profiles['player_id'], bat_profiles['sample_confidence']))
    bowl_conf_dict = dict(zip(bowl_profiles['player_id'], bowl_profiles['sample_confidence']))
    
    for pid in all_players['PlayerID']:
        is_b = pid in bat_pids
        is_bw = pid in bowl_pids
        if is_b and is_bw:
            roles.append("All-Rounder")
            is_dual.append(1)
        elif is_b:
            roles.append("Batter")
            is_dual.append(0)
        elif is_bw:
            roles.append("Bowler")
            is_dual.append(0)
        else:
            roles.append("Squad Member")
            is_dual.append(0)
            
        bat_conf.append(bat_conf_dict.get(pid, "Unqualified"))
        bowl_conf.append(bowl_conf_dict.get(pid, "Unqualified"))
        
    all_players['PrimaryRole'] = roles
    all_players['IsDualDiscipline'] = is_dual
    all_players['BattingConfidence'] = bat_conf
    all_players['BowlingConfidence'] = bowl_conf
    
    all_players.to_csv(os.path.join(DASHBOARD_DATA_DIR, "Dim_Player.csv"), index=False)
    print(f"  Saved Dim_Player: {len(all_players)} records")
    
    # ----------------------------------------------------
    # 5. BUILD DIM_PRESSURE_CONTEXT
    # ----------------------------------------------------
    print("[Step 5/7] Generating Dim_Pressure_Context...")
    dim_context = pd.DataFrame([
        {'ContextID': 1, 'ContextName': 'Chasing Clutch (Innings 2)', 'Discipline': 'Both', 'Description': 'High required run rate, steep par deficit, or critical wicket loss while chasing.'},
        {'ContextID': 2, 'ContextName': 'Collapse Recovery (Innings 1)', 'Discipline': 'Batting', 'Description': 'Early top-order loss (e.g. 3+ wickets down early) requiring crisis consolidation.'},
        {'ContextID': 3, 'ContextName': 'Death Overs Execution (Overs 17-20)', 'Discipline': 'Both', 'Description': 'Final phase acceleration for batters, boundary and yorker execution for bowlers.'},
        {'ContextID': 4, 'ContextName': 'Powerplay High-Leverage (Overs 1-6)', 'Discipline': 'Both', 'Description': 'Field restrictions and new ball execution with high swing/wicket stakes.'},
        {'ContextID': 5, 'ContextName': 'Middle Overs Tactical (Overs 7-16)', 'Discipline': 'Both', 'Description': 'Spin containment, rotation of strike, and boundary pacing under par deficit.'},
        {'ContextID': 6, 'ContextName': 'Normal Baseline Conditions', 'Discipline': 'Both', 'Description': 'Standard match conditions with low leverage and par required rates.'}
    ])
    dim_context.to_csv(os.path.join(DASHBOARD_DATA_DIR, "Dim_Pressure_Context.csv"), index=False)
    print(f"  Saved Dim_Pressure_Context: {len(dim_context)} records")
    
    # ----------------------------------------------------
    # 6. BUILD FACT_PLAYER_PRESSURE_SUMMARY
    # ----------------------------------------------------
    print("[Step 6/7] Generating Fact_Player_Pressure_Summary...")
    
    # Merge rankings, profiles, transferability, posterior, and consistency
    # Batters summary
    bat_summary = []
    for idx, row in bat_profiles.iterrows():
        pid = row['player_id']
        pname = row['player_name']
        
        # Check if in top 10
        top_match = top_bat[top_bat['player_id'] == pid]
        off_rank = int(top_match['pressure_rank'].values[0]) if len(top_match) > 0 else np.nan
        cpri = float(top_match['CPRI'].values[0]) if len(top_match) > 0 else np.nan
        cpri_low = float(top_match['cpri_ci_low'].values[0]) if len(top_match) > 0 else np.nan
        cpri_high = float(top_match['cpri_ci_high'].values[0]) if len(top_match) > 0 else np.nan
        cpri_width = (cpri_high - cpri_low) if not np.isnan(cpri_low) else np.nan
        
        # Transferability
        trans_match = trans_matrix[(trans_matrix['Player_Name'] == pname) & (trans_matrix['Discipline'] == 'Batter')]
        trans_prof = trans_match['Transferability_Classification'].values[0] if len(trans_match) > 0 else 'Unclassified'
        auc_risk = trans_match['Auction_Transferability_Risk'].values[0] if len(trans_match) > 0 else 'Unclassified'
        
        # Posterior
        post_match = post_probs[(post_probs['player_id'] == pid) & (post_probs['discipline'] == 'Batter')]
        med_rank = post_match['median_posterior_rank'].values[0] if len(post_match) > 0 else np.nan
        rank_ci_low = post_match['rank_95_ci_low'].values[0] if len(post_match) > 0 else np.nan
        rank_ci_high = post_match['rank_95_ci_high'].values[0] if len(post_match) > 0 else np.nan
        p_top10 = post_match['p_rank_le_10'].values[0] if len(post_match) > 0 else np.nan
        
        # Consistency
        cons_match = match_cons[(match_cons['player_id'] == pid) & (match_cons['discipline'] == 'Batter')]
        cv = cons_match['match_metric_cv'].values[0] if len(cons_match) > 0 else row.get('match_sr_cv', np.nan)
        succ = cons_match['match_success_rate'].values[0] if len(cons_match) > 0 else row.get('match_success_rate_140', np.nan)
        outlier_sens = cons_match['outlier_sensitivity_pct'].values[0] if len(cons_match) > 0 else np.nan
        cons_verdict = cons_match['consistency_verdict'].values[0] if len(cons_match) > 0 else 'Insufficient Matches'
        
        # Auction tier logic
        if off_rank in [1, 2, 3, 4]:
            auc_tier = "Tier 1: Marquee Clutch Finisher"
            purse_mult = "2.5x - 3.0x Baseline"
        elif off_rank in [5, 6, 7, 8, 9, 10]:
            auc_tier = "Tier 2: High-Upside Specialist"
            purse_mult = "1.8x - 2.2x Baseline"
        elif row['pressure_balls'] >= 50:
            auc_tier = "Tier 3: Core Tactical Asset"
            purse_mult = "1.2x - 1.5x Baseline"
        else:
            auc_tier = "Tier 4: Squad / Depth Player"
            purse_mult = "1.0x Baseline"
            
        bat_summary.append({
            'PlayerID': pid,
            'PlayerName': pname,
            'Discipline': 'Batter',
            'OfficialRank': off_rank,
            'CPRI': cpri,
            'CPRI_CI_Low': cpri_low,
            'CPRI_CI_High': cpri_high,
            'CPRI_CI_Width': cpri_width,
            'PressureBalls': row['pressure_balls'],
            'NormalBalls': row['normal_balls'],
            'PressurePerformance': round(row['raw_press_sr'], 2) if not pd.isna(row['raw_press_sr']) else 0.0,
            'NormalBaseline': round(row['norm_sr'], 2) if not pd.isna(row['norm_sr']) else 0.0,
            'DeltaContext': round(row['delta_context_sr'], 2) if not pd.isna(row['delta_context_sr']) else 0.0,
            'BayesEstimate': round(row['bayes_press_sr'], 2) if not pd.isna(row['bayes_press_sr']) else 0.0,
            'Bayes_CI_Low': round(row['bayes_sr_ci_low'], 2) if not pd.isna(row['bayes_sr_ci_low']) else 0.0,
            'Bayes_CI_High': round(row['bayes_sr_ci_high'], 2) if not pd.isna(row['bayes_sr_ci_high']) else 0.0,
            'Bayes_CI_Width': round(row['bayes_sr_ci_width'], 2) if not pd.isna(row['bayes_sr_ci_width']) else 0.0,
            'BoundaryPct': round(row['raw_press_boundary_pct'] * 100.0, 2) if not pd.isna(row['raw_press_boundary_pct']) else 0.0,
            'DotPct': round(row['raw_press_dot_pct'] * 100.0, 2) if not pd.isna(row['raw_press_dot_pct']) else 0.0,
            'DismissalOrWktRate': round(row['raw_press_dismissal_pct'] * 100.0, 2) if not pd.isna(row['raw_press_dismissal_pct']) else 0.0,
            'ConsistencyCV': round(cv, 4) if not pd.isna(cv) else np.nan,
            'MatchSuccessRate': round(succ * 100.0, 2) if not pd.isna(succ) else np.nan,
            'OutlierSensitivityPct': round(outlier_sens, 2) if not pd.isna(outlier_sens) else np.nan,
            'ConsistencyVerdict': cons_verdict,
            'TransferabilityProfile': trans_prof,
            'AuctionRisk': auc_risk,
            'MedianPosteriorRank': med_rank,
            'Rank_CI_Low': rank_ci_low,
            'Rank_CI_High': rank_ci_high,
            'ProbTop10': round(p_top10 * 100.0, 2) if not pd.isna(p_top10) else np.nan,
            'AuctionTier': auc_tier,
            'PurseMultiplier': purse_mult,
            'ConfidenceTier': row['sample_confidence']
        })

    # Bowlers summary
    bowl_summary = []
    for idx, row in bowl_profiles.iterrows():
        pid = row['player_id']
        pname = row['player_name']
        
        top_match = top_bowl[top_bowl['player_id'] == pid]
        off_rank = int(top_match['pressure_rank'].values[0]) if len(top_match) > 0 else np.nan
        cpri = float(top_match['CPRI'].values[0]) if len(top_match) > 0 else np.nan
        cpri_low = float(top_match['cpri_ci_low'].values[0]) if len(top_match) > 0 else np.nan
        cpri_high = float(top_match['cpri_ci_high'].values[0]) if len(top_match) > 0 else np.nan
        cpri_width = (cpri_high - cpri_low) if not np.isnan(cpri_low) else np.nan
        
        trans_match = trans_matrix[(trans_matrix['Player_Name'] == pname) & (trans_matrix['Discipline'] == 'Bowler')]
        trans_prof = trans_match['Transferability_Classification'].values[0] if len(trans_match) > 0 else 'Unclassified'
        auc_risk = trans_match['Auction_Transferability_Risk'].values[0] if len(trans_match) > 0 else 'Unclassified'
        
        post_match = post_probs[(post_probs['player_id'] == pid) & (post_probs['discipline'] == 'Bowler')]
        med_rank = post_match['median_posterior_rank'].values[0] if len(post_match) > 0 else np.nan
        rank_ci_low = post_match['rank_95_ci_low'].values[0] if len(post_match) > 0 else np.nan
        rank_ci_high = post_match['rank_95_ci_high'].values[0] if len(post_match) > 0 else np.nan
        p_top10 = post_match['p_rank_le_10'].values[0] if len(post_match) > 0 else np.nan
        
        cons_match = match_cons[(match_cons['player_id'] == pid) & (match_cons['discipline'] == 'Bowler')]
        cv = cons_match['match_metric_cv'].values[0] if len(cons_match) > 0 else row.get('match_econ_cv', np.nan)
        succ = cons_match['match_success_rate'].values[0] if len(cons_match) > 0 else row.get('match_success_rate_sub8', np.nan)
        outlier_sens = cons_match['outlier_sensitivity_pct'].values[0] if len(cons_match) > 0 else np.nan
        cons_verdict = cons_match['consistency_verdict'].values[0] if len(cons_match) > 0 else 'Insufficient Matches'
        
        if off_rank in [1, 2, 3, 4]:
            auc_tier = "Tier 1: Marquee Clutch Enforcer"
            purse_mult = "2.5x - 3.0x Baseline"
        elif off_rank in [5, 6, 7, 8, 9, 10]:
            auc_tier = "Tier 2: High-Upside Specialist"
            purse_mult = "1.8x - 2.2x Baseline"
        elif row['pressure_balls'] >= 60:
            auc_tier = "Tier 3: Core Tactical Asset"
            purse_mult = "1.2x - 1.5x Baseline"
        else:
            auc_tier = "Tier 4: Squad / Depth Player"
            purse_mult = "1.0x Baseline"
            
        bowl_summary.append({
            'PlayerID': pid,
            'PlayerName': pname,
            'Discipline': 'Bowler',
            'OfficialRank': off_rank,
            'CPRI': cpri,
            'CPRI_CI_Low': cpri_low,
            'CPRI_CI_High': cpri_high,
            'CPRI_CI_Width': cpri_width,
            'PressureBalls': row['pressure_balls'],
            'NormalBalls': row['normal_balls'],
            'PressurePerformance': round(row['raw_press_econ'], 2) if not pd.isna(row['raw_press_econ']) else 0.0,
            'NormalBaseline': round(row['norm_econ'], 2) if not pd.isna(row['norm_econ']) else 0.0,
            'DeltaContext': round(row['delta_context_econ'], 2) if not pd.isna(row['delta_context_econ']) else 0.0,
            'BayesEstimate': round(row['bayes_press_econ'], 2) if not pd.isna(row['bayes_press_econ']) else 0.0,
            'Bayes_CI_Low': round(row['bayes_econ_ci_low'], 2) if not pd.isna(row['bayes_econ_ci_low']) else 0.0,
            'Bayes_CI_High': round(row['bayes_econ_ci_high'], 2) if not pd.isna(row['bayes_econ_ci_high']) else 0.0,
            'Bayes_CI_Width': round(row['bayes_econ_ci_width'], 2) if not pd.isna(row['bayes_econ_ci_width']) else 0.0,
            'BoundaryPct': round(row['raw_press_boundary_pct'] * 100.0, 2) if not pd.isna(row['raw_press_boundary_pct']) else 0.0,
            'DotPct': round(row['raw_press_dot_pct'] * 100.0, 2) if not pd.isna(row['raw_press_dot_pct']) else 0.0,
            'DismissalOrWktRate': round(row['raw_press_wicket_pct'] * 100.0, 2) if not pd.isna(row['raw_press_wicket_pct']) else 0.0,
            'ConsistencyCV': round(cv, 4) if not pd.isna(cv) else np.nan,
            'MatchSuccessRate': round(succ * 100.0, 2) if not pd.isna(succ) else np.nan,
            'OutlierSensitivityPct': round(outlier_sens, 2) if not pd.isna(outlier_sens) else np.nan,
            'ConsistencyVerdict': cons_verdict,
            'TransferabilityProfile': trans_prof,
            'AuctionRisk': auc_risk,
            'MedianPosteriorRank': med_rank,
            'Rank_CI_Low': rank_ci_low,
            'Rank_CI_High': rank_ci_high,
            'ProbTop10': round(p_top10 * 100.0, 2) if not pd.isna(p_top10) else np.nan,
            'AuctionTier': auc_tier,
            'PurseMultiplier': purse_mult,
            'ConfidenceTier': row['sample_confidence']
        })
        
    fact_summary = pd.DataFrame(bat_summary + bowl_summary)
    fact_summary.to_csv(os.path.join(DASHBOARD_DATA_DIR, "Fact_Player_Pressure_Summary.csv"), index=False)
    print(f"  Saved Fact_Player_Pressure_Summary: {len(fact_summary)} records")
    
    # ----------------------------------------------------
    # 7. BUILD FACT_MATCH_PLAYER_PERFORMANCE & SITUATION SPLITS
    # ----------------------------------------------------
    print("[Step 7/7] Generating Fact_Match_Player_Performance & Fact_Situation_Splits...")
    
    # Batter match performances
    bat_legal = deliv_features[deliv_features['is_legal'] == 1].copy()
    
    bat_match_perf = bat_legal.groupby(['match_id', 'striker_id', 'is_bat_pressure']).agg(
        Balls=('runs', 'count'),
        Runs=('runs', 'sum'),
        Outs=('is_wicket', 'sum'),
        Boundaries=('is_four', lambda x: (x == 1).sum() + (bat_legal.loc[x.index, 'is_six'] == 1).sum()),
        Dots=('runs', lambda x: (x == 0).sum())
    ).reset_index()
    bat_match_perf.rename(columns={'striker_id': 'PlayerID', 'match_id': 'MatchID', 'is_bat_pressure': 'IsPressureState'}, inplace=True)
    bat_match_perf['Discipline'] = 'Batter'
    bat_match_perf['RateMetric'] = (bat_match_perf['Runs'] / bat_match_perf['Balls']) * 100.0
    
    # Bowler match performances
    bowl_legal = deliv_features[deliv_features['is_legal'] == 1].copy()
    bowl_match_perf = bowl_legal.groupby(['match_id', 'bowler_id', 'is_bowl_leverage']).agg(
        Balls=('bowler_runs_conceded', 'count'),
        Runs=('bowler_runs_conceded', 'sum'),
        Outs=('is_bowler_wicket', 'sum'),
        Boundaries=('is_four', lambda x: (x == 1).sum() + (bowl_legal.loc[x.index, 'is_six'] == 1).sum()),
        Dots=('bowler_runs_conceded', lambda x: (x == 0).sum())
    ).reset_index()
    bowl_match_perf.rename(columns={'bowler_id': 'PlayerID', 'match_id': 'MatchID', 'is_bowl_leverage': 'IsPressureState'}, inplace=True)
    bowl_match_perf['Discipline'] = 'Bowler'
    bowl_match_perf['RateMetric'] = (bowl_match_perf['Runs'] / bowl_match_perf['Balls']) * 6.0
    
    comb_match_perf = pd.concat([bat_match_perf, bowl_match_perf], ignore_index=True)
    comb_match_perf.to_csv(os.path.join(DASHBOARD_DATA_DIR, "Fact_Match_Player_Performance.csv"), index=False)
    print(f"  Saved Fact_Match_Player_Performance: {len(comb_match_perf)} records")
    
    # Situation splits
    # Chasing Clutch, Collapse Recovery, Death Overs, Normal
    # For Top players
    splits = []
    top_pids = set(top_bat['player_id']).union(set(top_bowl['player_id']))
    
    for pid in top_pids:
        # Batter splits
        p_bat = bat_legal[bat_legal['striker_id'] == pid]
        if len(p_bat) > 0:
            for sit_name, mask in [
                ('Chasing Clutch', p_bat['is_bat_chasing_clutch'] == 1),
                ('Collapse Recovery', p_bat['is_collapse_crisis'] == 1),
                ('Death Overs', p_bat['is_death_overs'] == 1),
                ('Normal Baseline', p_bat['is_bat_normal'] == 1)
            ]:
                sub = p_bat[mask]
                b = len(sub)
                r = sub['runs'].sum()
                o = sub['is_wicket'].sum()
                bnd = sub['is_four'].sum() + sub['is_six'].sum()
                dt = (sub['runs'] == 0).sum()
                rate = (r / b * 100.0) if b > 0 else 0.0
                splits.append({
                    'PlayerID': pid,
                    'Discipline': 'Batter',
                    'Situation': sit_name,
                    'Balls': b,
                    'Runs': r,
                    'DismissalsOrWickets': o,
                    'RateMetric': round(rate, 2),
                    'BoundaryPct': round(bnd / b * 100.0, 2) if b > 0 else 0.0,
                    'DotPct': round(dt / b * 100.0, 2) if b > 0 else 0.0
                })
                
        # Bowler splits
        p_bowl = bowl_legal[bowl_legal['bowler_id'] == pid]
        if len(p_bowl) > 0:
            for sit_name, mask in [
                ('Chasing Clutch (Defending)', p_bowl['is_bat_chasing_clutch'] == 1),
                ('Death Overs Execution', p_bowl['is_death_overs'] == 1),
                ('Normal Baseline', p_bowl['is_bowl_normal'] == 1)
            ]:
                sub = p_bowl[mask]
                b = len(sub)
                r = sub['bowler_runs_conceded'].sum()
                w = sub['is_bowler_wicket'].sum()
                bnd = sub['is_four'].sum() + sub['is_six'].sum()
                dt = (sub['bowler_runs_conceded'] == 0).sum()
                rate = (r / b * 6.0) if b > 0 else 0.0
                splits.append({
                    'PlayerID': pid,
                    'Discipline': 'Bowler',
                    'Situation': sit_name,
                    'Balls': b,
                    'Runs': r,
                    'DismissalsOrWickets': w,
                    'RateMetric': round(rate, 2),
                    'BoundaryPct': round(bnd / b * 100.0, 2) if b > 0 else 0.0,
                    'DotPct': round(dt / b * 100.0, 2) if b > 0 else 0.0
                })
                
    fact_splits = pd.DataFrame(splits)
    fact_splits.to_csv(os.path.join(DASHBOARD_DATA_DIR, "Fact_Situation_Splits.csv"), index=False)
    print(f"  Saved Fact_Situation_Splits: {len(fact_splits)} records")
    
    print("\n[SUCCESS] All 7 Star-Schema tables exported to: " + DASHBOARD_DATA_DIR)

if __name__ == '__main__':
    build_and_export_powerbi_tables()
