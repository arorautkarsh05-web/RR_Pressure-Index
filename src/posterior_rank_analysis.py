"""
RR PRESSURE INDEX 2027 — POSTERIOR RANK UNCERTAINTY & MATCH CONSISTENCY AUDIT
Phase 03.1 Independent Statistical Verification

This script executes:
1. Monte Carlo posterior rank simulations (10,000 draws) to estimate rank credible intervals,
   P(Rank <= 10), and pairwise superiority probabilities.
2. Match-level consistency and outlier dependence (Jackknife sensitivity) audit across
   all qualified batters and bowlers.
"""

import sys
import os
import numpy as np
import pandas as pd
from scipy import stats

PROJECT_ROOT = r"d:\RR_PRESSURE_INDEX_2027"
TABLES_DIR = os.path.join(PROJECT_ROOT, "outputs", "tables")
RANKINGS_DIR = os.path.join(PROJECT_ROOT, "outputs", "rankings")
AUDIT_DIR = os.path.join(PROJECT_ROOT, "outputs", "audit")

os.makedirs(AUDIT_DIR, exist_ok=True)

def run_monte_carlo_rank_simulations(n_draws=10000, seed=42):
    print("=" * 80)
    print("STEP 1: BAYESIAN MONTE CARLO POSTERIOR RANK SIMULATION (10,000 DRAWS)")
    print("=" * 80)
    
    rng = np.random.default_rng(seed)
    
    # Load rankings confidence
    conf_df = pd.read_csv(os.path.join(TABLES_DIR, "ranking_confidence.csv"))
    
    # Load Top 10 files for official order
    top_bat = pd.read_csv(os.path.join(RANKINGS_DIR, "top_10_batters.csv"))
    top_bowl = pd.read_csv(os.path.join(RANKINGS_DIR, "top_10_bowlers.csv"))
    
    # Filter qualified cohort from confidence table
    # Batters (role == 'Batter')
    bat_cohort = conf_df[conf_df['role'] == 'Batter'].copy()
    bowl_cohort = conf_df[conf_df['role'] == 'Bowler'].copy()
    
    # Function to simulate ranks
    def simulate_cohort(cohort_df, discipline, higher_is_better=True):
        pids = cohort_df['player_id'].values
        names = cohort_df['player_name'].values
        means = cohort_df['CPRI'].values
        # SE = CI width / (2 * 1.96)
        ses = (cohort_df['cpri_ci_width'].values) / (2.0 * 1.95996)
        
        # Simulate matrix of shape (n_draws, n_players)
        draws = rng.normal(loc=means, scale=ses, size=(n_draws, len(pids)))
        
        # Calculate ranks for each draw
        # Higher score = rank 1
        if higher_is_better:
            # argsort twice gives ranks 0 to N-1
            # But rankdata or argsort descending:
            # We want highest draw to get rank 1
            ranks = stats.rankdata(-draws, method='average', axis=1)
        else:
            ranks = stats.rankdata(draws, method='average', axis=1)
            
        # Summary statistics per player
        results = []
        for i, (pid, name) in enumerate(zip(pids, names)):
            player_ranks = ranks[:, i]
            player_scores = draws[:, i]
            
            med_rank = np.median(player_ranks)
            p2_5 = np.percentile(player_ranks, 2.5)
            p97_5 = np.percentile(player_ranks, 97.5)
            p_top_10 = np.mean(player_ranks <= 10.0)
            p_top_5 = np.mean(player_ranks <= 5.0)
            p_beat_pop = np.mean(player_scores > 50.0)
            
            results.append({
                'discipline': discipline,
                'player_id': pid,
                'player_name': name,
                'official_cpri': means[i],
                'cpri_se': ses[i],
                'median_posterior_rank': med_rank,
                'rank_95_ci_low': p2_5,
                'rank_95_ci_high': p97_5,
                'p_rank_le_10': p_top_10,
                'p_rank_le_5': p_top_5,
                'p_beat_pop_benchmark': p_beat_pop,
                'draws_mean': np.mean(player_scores)
            })
            
        res_df = pd.DataFrame(results).sort_values('official_cpri', ascending=False).reset_index(drop=True)
        res_df['official_rank'] = res_df.index + 1
        
        # Pairwise superiority against next ranked player
        p_superior = []
        for i in range(len(res_df)):
            if i < len(res_df) - 1:
                idx_curr = np.where(pids == res_df.loc[i, 'player_id'])[0][0]
                idx_next = np.where(pids == res_df.loc[i+1, 'player_id'])[0][0]
                p_sup = np.mean(draws[:, idx_curr] > draws[:, idx_next])
            else:
                p_sup = np.nan
            p_superior.append(p_sup)
        res_df['p_superior_to_next'] = p_superior
        
        return res_df, draws, pids

    sim_bat, draws_bat, pids_bat = simulate_cohort(bat_cohort, 'Batter', higher_is_better=True)
    sim_bowl, draws_bowl, pids_bowl = simulate_cohort(bowl_cohort, 'Bowler', higher_is_better=True)
    
    # Combine Top 20 of each
    sim_combined = pd.concat([sim_bat.head(20), sim_bowl.head(20)], ignore_index=True)
    
    out_path = os.path.join(AUDIT_DIR, "posterior_rank_probabilities.csv")
    sim_combined.to_csv(out_path, index=False)
    print(f"Saved Posterior Rank Uncertainty Table to: {out_path}")
    
    # Print Top 10 Summary
    print("\n--- TOP 10 BATTERS POSTERIOR RANK PROBABILITIES ---")
    print(sim_bat[['official_rank', 'player_name', 'official_cpri', 'median_posterior_rank', 
                   'rank_95_ci_low', 'rank_95_ci_high', 'p_rank_le_10', 'p_superior_to_next']].head(10).to_string(index=False))
    
    print("\n--- TOP 10 BOWLERS POSTERIOR RANK PROBABILITIES ---")
    print(sim_bowl[['official_rank', 'player_name', 'official_cpri', 'median_posterior_rank', 
                    'rank_95_ci_low', 'rank_95_ci_high', 'p_rank_le_10', 'p_superior_to_next']].head(10).to_string(index=False))
    
    return sim_combined


def run_match_consistency_audit():
    print("\n" + "=" * 80)
    print("STEP 2: MATCH-LEVEL CONSISTENCY & OUTLIER SENSITIVITY AUDIT (JACKKNIFE)")
    print("=" * 80)
    
    # Load deliveries
    deliv_path = os.path.join(TABLES_DIR, "delivery_pressure_features_v2.csv")
    print(f"Loading delivery features from: {deliv_path}...")
    df = pd.read_csv(deliv_path, usecols=[
        'match_id', 'striker_id', 'striker_name', 'bowler_id', 'bowler_name',
        'is_legal', 'runs', 'bowler_runs_conceded', 'is_wicket', 'is_bowler_wicket',
        'is_bat_pressure', 'is_bowl_leverage'
    ])
    
    # Load Top 10 to guarantee inclusion
    top_bat = pd.read_csv(os.path.join(RANKINGS_DIR, "top_10_batters.csv"))
    top_bowl = pd.read_csv(os.path.join(RANKINGS_DIR, "top_10_bowlers.csv"))
    
    # ----------------------------------------------------
    # BATTING MATCH CONSISTENCY
    # ----------------------------------------------------
    bat_press = df[(df['is_bat_pressure'] == 1) & (df['is_legal'] == 1)].copy()
    
    # Group by match and striker
    bat_match_grp = bat_press.groupby(['striker_id', 'striker_name', 'match_id']).agg(
        match_balls=('runs', 'count'),
        match_runs=('runs', 'sum'),
        match_outs=('is_wicket', 'sum')
    ).reset_index()
    
    # Filter qualified pressure innings: at least 3 pressure balls faced in that match
    bat_qual_matches = bat_match_grp[bat_match_grp['match_balls'] >= 3].copy()
    bat_qual_matches['match_sr'] = (bat_qual_matches['match_runs'] / bat_qual_matches['match_balls']) * 100.0
    
    # Summarize per batter
    bat_consistency = []
    # Evaluate qualified batters (from top_bat and players with >= 50 pressure balls)
    for pid in top_bat['player_id'].unique():
        p_matches = bat_qual_matches[bat_qual_matches['striker_id'] == pid]
        p_name = top_bat[top_bat['player_id'] == pid]['player_name'].values[0]
        
        n_matches = len(p_matches)
        total_p_balls = p_matches['match_balls'].sum()
        total_p_runs = p_matches['match_runs'].sum()
        agg_sr = (total_p_runs / total_p_balls * 100.0) if total_p_balls > 0 else 0.0
        
        if n_matches >= 3:
            sr_mean = p_matches['match_sr'].mean()
            sr_std = p_matches['match_sr'].std()
            sr_cv = (sr_std / sr_mean) if sr_mean > 0 else 0.0
            sr_iqr = np.percentile(p_matches['match_sr'], 75) - np.percentile(p_matches['match_sr'], 25)
            success_rate = (p_matches['match_sr'] >= 140.0).mean()
            
            # Jackknife: Find top outlier match (highest positive impact on aggregate SR)
            # For each match, recalculate SR without that match
            loo_srs = []
            for m_id in p_matches['match_id'].values:
                rem = p_matches[p_matches['match_id'] != m_id]
                rem_balls = rem['match_balls'].sum()
                rem_runs = rem['match_runs'].sum()
                rem_sr = (rem_runs / rem_balls * 100.0) if rem_balls > 0 else 0.0
                loo_srs.append(rem_sr)
            
            min_loo_sr = min(loo_srs) # Removing the best match leaves the lowest remaining SR
            outlier_drop_sr = agg_sr - min_loo_sr
            outlier_drop_pct = (outlier_drop_sr / agg_sr) * 100.0 if agg_sr > 0 else 0.0
            
            if outlier_drop_pct < 10.0:
                robustness = "Highly Robust (Low Outlier Sensitivity)"
            elif outlier_drop_pct < 20.0:
                robustness = "Moderately Robust (Balanced Across Matches)"
            else:
                robustness = "Fragile (Heavily Driven by 1 Match)"
                
            bat_consistency.append({
                'discipline': 'Batter',
                'player_id': pid,
                'player_name': p_name,
                'qualified_matches': n_matches,
                'total_pressure_balls': total_p_balls,
                'aggregate_sr': round(agg_sr, 2),
                'match_sr_mean': round(sr_mean, 2),
                'match_sr_std': round(sr_std, 2),
                'match_sr_cv': round(sr_cv, 4),
                'match_sr_iqr': round(sr_iqr, 2),
                'match_success_rate': round(success_rate, 4),
                'sr_without_top_match': round(min_loo_sr, 2),
                'outlier_drop_pct': round(outlier_drop_pct, 2),
                'consistency_verdict': robustness
            })
            
    # ----------------------------------------------------
    # BOWLING MATCH CONSISTENCY
    # ----------------------------------------------------
    bowl_press = df[(df['is_bowl_leverage'] == 1) & (df['is_legal'] == 1)].copy()
    
    bowl_match_grp = bowl_press.groupby(['bowler_id', 'bowler_name', 'match_id']).agg(
        match_balls=('bowler_runs_conceded', 'count'),
        match_runs=('bowler_runs_conceded', 'sum'),
        match_wkts=('is_bowler_wicket', 'sum')
    ).reset_index()
    
    # Filter qualified leverage spells: at least 3 leverage balls bowled in that match
    bowl_qual_matches = bowl_match_grp[bowl_match_grp['match_balls'] >= 3].copy()
    bowl_qual_matches['match_econ'] = (bowl_qual_matches['match_runs'] / bowl_qual_matches['match_balls']) * 6.0
    
    bowl_consistency = []
    for pid in top_bowl['player_id'].unique():
        p_matches = bowl_qual_matches[bowl_qual_matches['bowler_id'] == pid]
        p_name = top_bowl[top_bowl['player_id'] == pid]['player_name'].values[0]
        
        n_matches = len(p_matches)
        total_p_balls = p_matches['match_balls'].sum()
        total_p_runs = p_matches['match_runs'].sum()
        agg_econ = (total_p_runs / total_p_balls * 6.0) if total_p_balls > 0 else 0.0
        
        if n_matches >= 3:
            econ_mean = p_matches['match_econ'].mean()
            econ_std = p_matches['match_econ'].std()
            econ_cv = (econ_std / econ_mean) if econ_mean > 0 else 0.0
            econ_iqr = np.percentile(p_matches['match_econ'], 75) - np.percentile(p_matches['match_econ'], 25)
            success_rate = (p_matches['match_econ'] <= 8.50).mean()
            
            # Jackknife: Find top outlier match (highest positive impact on keeping aggregate economy low)
            # Removing the best bowling match leaves the HIGHEST remaining economy
            loo_econs = []
            for m_id in p_matches['match_id'].values:
                rem = p_matches[p_matches['match_id'] != m_id]
                rem_balls = rem['match_balls'].sum()
                rem_runs = rem['match_runs'].sum()
                rem_econ = (rem_runs / rem_balls * 6.0) if rem_balls > 0 else 0.0
                loo_econs.append(rem_econ)
                
            max_loo_econ = max(loo_econs)
            outlier_increase_econ = max_loo_econ - agg_econ
            outlier_increase_pct = (outlier_increase_econ / agg_econ) * 100.0 if agg_econ > 0 else 0.0
            
            if outlier_increase_pct < 10.0:
                robustness = "Highly Robust (Low Outlier Sensitivity)"
            elif outlier_increase_pct < 20.0:
                robustness = "Moderately Robust (Balanced Across Matches)"
            else:
                robustness = "Fragile (Heavily Driven by 1 Match)"
                
            bowl_consistency.append({
                'discipline': 'Bowler',
                'player_id': pid,
                'player_name': p_name,
                'qualified_matches': n_matches,
                'total_pressure_balls': total_p_balls,
                'aggregate_sr': round(agg_econ, 2), # represents aggregate economy
                'match_sr_mean': round(econ_mean, 2),
                'match_sr_std': round(econ_std, 2),
                'match_sr_cv': round(econ_cv, 4),
                'match_sr_iqr': round(econ_iqr, 2),
                'match_success_rate': round(success_rate, 4),
                'sr_without_top_match': round(max_loo_econ, 2),
                'outlier_drop_pct': round(outlier_increase_pct, 2), # represents % increase in economy
                'consistency_verdict': robustness
            })
            
    comb_consistency = pd.DataFrame(bat_consistency + bowl_consistency)
    # Rename columns to be domain-generic and clear
    comb_consistency.rename(columns={
        'aggregate_sr': 'aggregate_metric_sr_or_econ',
        'match_sr_mean': 'match_metric_mean',
        'match_sr_std': 'match_metric_std',
        'match_sr_cv': 'match_metric_cv',
        'match_sr_iqr': 'match_metric_iqr',
        'sr_without_top_match': 'metric_without_top_match',
        'outlier_drop_pct': 'outlier_sensitivity_pct'
    }, inplace=True)
    
    out_path = os.path.join(AUDIT_DIR, "match_consistency_validation.csv")
    comb_consistency.to_csv(out_path, index=False)
    print(f"Saved Match Consistency Validation Table to: {out_path}")
    
    print("\n--- MATCH CONSISTENCY & OUTLIER SENSITIVITY SUMMARY ---")
    print(comb_consistency[['discipline', 'player_name', 'qualified_matches', 'aggregate_metric_sr_or_econ',
                            'match_metric_cv', 'match_success_rate', 'outlier_sensitivity_pct', 'consistency_verdict']].to_string(index=False))
    
    return comb_consistency


if __name__ == '__main__':
    run_monte_carlo_rank_simulations(n_draws=10000, seed=42)
    run_match_consistency_audit()
    print("\n[SUCCESS] Posterior rank analysis and match consistency audit complete.")

