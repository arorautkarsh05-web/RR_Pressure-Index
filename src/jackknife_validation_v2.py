"""
RR PRESSURE INDEX 2027 — FULL JACKKNIFE VALIDATION & POSTERIOR INTERPRETATION AUDIT
Phase 03.2 Final Statistical Audit

This script performs:
1. True Leave-One-Match-Out (LOMO) Jackknife across all matches for Top 10 Batters and Bowlers.
   - Calculates Jackknife SE, worst-case metric, best-case metric, max rank drop, and most influential match.
2. Posterior Rank Interpretation Audit:
   - Evaluates P(Rank = 1), P(Rank <= 3), P(Rank <= 5), P(Rank <= 10), median rank, and 95% intervals.
   - Formulates strict linguistic and interpretation rules to prevent misleading claims.
"""

import os
import sys
import numpy as np
import pandas as pd
from scipy import stats

PROJECT_ROOT = r"d:\RR_PRESSURE_INDEX_2027"
TABLES_DIR = os.path.join(PROJECT_ROOT, "outputs", "tables")
RANKINGS_DIR = os.path.join(PROJECT_ROOT, "outputs", "rankings")
AUDIT_DIR = os.path.join(PROJECT_ROOT, "outputs", "audit")

os.makedirs(AUDIT_DIR, exist_ok=True)

def run_full_jackknife_and_posterior_audit(n_draws=10000, seed=42):
    print("=" * 80)
    print("STEP 1: FULL LEAVE-ONE-MATCH-OUT (LOMO) JACKKNIFE VALIDATION")
    print("=" * 80)
    
    deliv_features = pd.read_csv(os.path.join(TABLES_DIR, "delivery_pressure_features_v2.csv"), usecols=[
        'match_id', 'striker_id', 'striker_name', 'bowler_id', 'bowler_name',
        'is_legal', 'runs', 'bowler_runs_conceded', 'is_bat_pressure', 'is_bowl_leverage'
    ])
    
    top_bat = pd.read_csv(os.path.join(RANKINGS_DIR, "top_10_batters.csv"))
    top_bowl = pd.read_csv(os.path.join(RANKINGS_DIR, "top_10_bowlers.csv"))
    
    # ----------------------------------------------------
    # A. BATTERS FULL LOMO JACKKNIFE
    # ----------------------------------------------------
    bat_legal = deliv_features[(deliv_features['is_bat_pressure'] == 1) & (deliv_features['is_legal'] == 1)].copy()
    
    bat_match_grp = bat_legal.groupby(['striker_id', 'striker_name', 'match_id']).agg(
        m_balls=('runs', 'count'),
        m_runs=('runs', 'sum')
    ).reset_index()
    
    jack_results = []
    
    # Base rates for top batters
    base_bat_rates = {}
    for pid in top_bat['player_id']:
        p_df = bat_legal[bat_legal['striker_id'] == pid]
        base_bat_rates[pid] = (p_df['runs'].sum() / len(p_df) * 100.0) if len(p_df) > 0 else 0.0
        
    for idx, row in top_bat.iterrows():
        pid = row['player_id']
        pname = row['player_name']
        off_rank = row['pressure_rank']
        base_rate = base_bat_rates[pid]
        
        p_matches = bat_match_grp[bat_match_grp['striker_id'] == pid].copy()
        # Filter qualified matches (>= 3 pressure balls)
        p_qual = p_matches[p_matches['m_balls'] >= 3].reset_index(drop=True)
        M = len(p_qual)
        
        if M < 2:
            continue
            
        loo_rates = []
        influences = []
        
        tot_balls = p_matches['m_balls'].sum()
        tot_runs = p_matches['m_runs'].sum()
        
        for m_idx, m_row in p_qual.iterrows():
            m_id = m_row['match_id']
            # Remove this match from total
            rem_balls = tot_balls - m_row['m_balls']
            rem_runs = tot_runs - m_row['m_runs']
            rem_rate = (rem_runs / rem_balls * 100.0) if rem_balls > 0 else 0.0
            loo_rates.append(rem_rate)
            influences.append((m_id, abs(rem_rate - base_rate), rem_rate - base_rate))
            
        loo_rates = np.array(loo_rates)
        jack_mean = np.mean(loo_rates)
        jack_se = np.sqrt(((M - 1) / M) * np.sum((loo_rates - jack_mean) ** 2))
        
        worst_case_rate = np.min(loo_rates) # removing best match leaves lowest SR
        best_case_rate = np.max(loo_rates)  # removing worst match leaves highest SR
        max_negative_impact = np.min(loo_rates) - base_rate
        max_positive_impact = np.max(loo_rates) - base_rate
        
        # Identify highest leverage match
        influences.sort(key=lambda x: x[1], reverse=True)
        top_inf_mid, top_inf_abs, top_inf_delta = influences[0]
        
        # Calculate worst-case rank within Top 10
        # If player's rate dropped to worst_case_rate, what would their rank be against other players' base rates?
        sim_rates = base_bat_rates.copy()
        sim_rates[pid] = worst_case_rate
        sim_series = pd.Series(sim_rates)
        worst_case_rank = int(sim_series.rank(ascending=False)[pid])
        max_rank_drop = worst_case_rank - off_rank
        
        jack_results.append({
            'discipline': 'Batter',
            'official_rank': off_rank,
            'player_id': pid,
            'player_name': pname,
            'qualified_matches_count': M,
            'baseline_metric': round(base_rate, 2),
            'jackknife_mean': round(jack_mean, 2),
            'jackknife_se': round(jack_se, 2),
            'worst_case_metric_lomo': round(worst_case_rate, 2),
            'best_case_metric_lomo': round(best_case_rate, 2),
            'max_negative_shift': round(max_negative_impact, 2),
            'max_positive_shift': round(max_positive_impact, 2),
            'worst_case_rank_lomo': worst_case_rank,
            'max_rank_degradation': max_rank_drop,
            'most_influential_match_id': top_inf_mid,
            'influential_match_shift': round(top_inf_delta, 2),
            'jackknife_verdict': 'Highly Resilient' if max_rank_drop <= 2 else 'Moderately Sensitive'
        })

    # ----------------------------------------------------
    # B. BOWLERS FULL LOMO JACKKNIFE
    # ----------------------------------------------------
    bowl_legal = deliv_features[(deliv_features['is_bowl_leverage'] == 1) & (deliv_features['is_legal'] == 1)].copy()
    
    bowl_match_grp = bowl_legal.groupby(['bowler_id', 'bowler_name', 'match_id']).agg(
        m_balls=('bowler_runs_conceded', 'count'),
        m_runs=('bowler_runs_conceded', 'sum')
    ).reset_index()
    
    base_bowl_rates = {}
    for pid in top_bowl['player_id']:
        p_df = bowl_legal[bowl_legal['bowler_id'] == pid]
        base_bowl_rates[pid] = (p_df['bowler_runs_conceded'].sum() / len(p_df) * 6.0) if len(p_df) > 0 else 0.0
        
    for idx, row in top_bowl.iterrows():
        pid = row['player_id']
        pname = row['player_name']
        off_rank = row['pressure_rank']
        base_rate = base_bowl_rates[pid]
        
        p_matches = bowl_match_grp[bowl_match_grp['bowler_id'] == pid].copy()
        p_qual = p_matches[p_matches['m_balls'] >= 3].reset_index(drop=True)
        M = len(p_qual)
        
        if M < 2:
            continue
            
        loo_rates = []
        influences = []
        
        tot_balls = p_matches['m_balls'].sum()
        tot_runs = p_matches['m_runs'].sum()
        
        for m_idx, m_row in p_qual.iterrows():
            m_id = m_row['match_id']
            rem_balls = tot_balls - m_row['m_balls']
            rem_runs = tot_runs - m_row['m_runs']
            rem_rate = (rem_runs / rem_balls * 6.0) if rem_balls > 0 else 0.0
            loo_rates.append(rem_rate)
            influences.append((m_id, abs(rem_rate - base_rate), rem_rate - base_rate))
            
        loo_rates = np.array(loo_rates)
        jack_mean = np.mean(loo_rates)
        jack_se = np.sqrt(((M - 1) / M) * np.sum((loo_rates - jack_mean) ** 2))
        
        worst_case_rate = np.max(loo_rates) # removing best match leaves highest economy (worst)
        best_case_rate = np.min(loo_rates)  # removing worst match leaves lowest economy (best)
        max_negative_impact = np.max(loo_rates) - base_rate # increase in econ
        max_positive_impact = np.min(loo_rates) - base_rate # decrease in econ
        
        influences.sort(key=lambda x: x[1], reverse=True)
        top_inf_mid, top_inf_abs, top_inf_delta = influences[0]
        
        # Worst case rank in bowling: lower econ is better rank
        sim_rates = base_bowl_rates.copy()
        sim_rates[pid] = worst_case_rate
        sim_series = pd.Series(sim_rates)
        worst_case_rank = int(sim_series.rank(ascending=True)[pid])
        max_rank_drop = worst_case_rank - off_rank
        
        jack_results.append({
            'discipline': 'Bowler',
            'official_rank': off_rank,
            'player_id': pid,
            'player_name': pname,
            'qualified_matches_count': M,
            'baseline_metric': round(base_rate, 2),
            'jackknife_mean': round(jack_mean, 2),
            'jackknife_se': round(jack_se, 2),
            'worst_case_metric_lomo': round(worst_case_rate, 2),
            'best_case_metric_lomo': round(best_case_rate, 2),
            'max_negative_shift': round(max_negative_impact, 2),
            'max_positive_shift': round(max_positive_impact, 2),
            'worst_case_rank_lomo': worst_case_rank,
            'max_rank_degradation': max_rank_drop,
            'most_influential_match_id': top_inf_mid,
            'influential_match_shift': round(top_inf_delta, 2),
            'jackknife_verdict': 'Highly Resilient' if max_rank_drop <= 2 else 'Moderately Sensitive'
        })
        
    jack_df = pd.DataFrame(jack_results)
    out_jack_path = os.path.join(AUDIT_DIR, "jackknife_full_results.csv")
    jack_df.to_csv(out_jack_path, index=False)
    print(f"Exported Full LOMO Jackknife Table to: {out_jack_path}")
    
    print("\n=== FULL LOMO JACKKNIFE RESULTS TABLE ===")
    print(jack_df[['discipline', 'official_rank', 'player_name', 'qualified_matches_count', 
                   'baseline_metric', 'jackknife_se', 'worst_case_metric_lomo', 'worst_case_rank_lomo', 
                   'max_rank_degradation', 'jackknife_verdict']].to_string(index=False))
    
    # ----------------------------------------------------
    # STEP 2: POSTERIOR RANK PROBABILITIES & LINGUISTIC AUDIT
    # ----------------------------------------------------
    print("\n" + "=" * 80)
    print("STEP 2: POSTERIOR RANK INTERPRETATION & LINGUISTIC AUDIT")
    print("=" * 80)
    
    rng = np.random.default_rng(seed)
    conf_df = pd.read_csv(os.path.join(TABLES_DIR, "ranking_confidence.csv"))
    
    def simulate_posterior_details(cohort_df, discipline):
        pids = cohort_df['player_id'].values
        names = cohort_df['player_name'].values
        means = cohort_df['CPRI'].values
        ses = (cohort_df['cpri_ci_width'].values) / (2.0 * 1.95996)
        
        draws = rng.normal(loc=means, scale=ses, size=(n_draws, len(pids)))
        ranks = stats.rankdata(-draws, method='average', axis=1) # rank 1 is highest score
        
        post_audit = []
        for i in range(min(10, len(pids))):
            r_i = ranks[:, i]
            p_rank1 = np.mean(r_i == 1.0)
            p_top3 = np.mean(r_i <= 3.0)
            p_top5 = np.mean(r_i <= 5.0)
            p_top10 = np.mean(r_i <= 10.0)
            med_r = np.median(r_i)
            ci_low = np.percentile(r_i, 2.5)
            ci_high = np.percentile(r_i, 97.5)
            
            # Linguistic directive
            if p_rank1 >= 0.70:
                ling_directive = "Permitted: 'Decisive statistical leader'"
            elif p_top3 >= 0.70:
                ling_directive = "Permitted: 'Leading contender within elite tier' (FORBIDDEN: 'Undisputed #1')"
            elif p_top10 >= 0.70:
                ling_directive = "Permitted: 'Certified Top 10 asset' (FORBIDDEN: 'Definitive rank position')"
            else:
                ling_directive = "Permitted: 'Provisional Top 10 contender with wide interval'"
                
            post_audit.append({
                'discipline': discipline,
                'official_rank': i + 1,
                'player_id': pids[i],
                'player_name': names[i],
                'official_cpri': means[i],
                'p_rank_1_pct': round(p_rank1 * 100.0, 2),
                'p_rank_le_3_pct': round(p_top3 * 100.0, 2),
                'p_rank_le_5_pct': round(p_top5 * 100.0, 2),
                'p_rank_le_10_pct': round(p_top10 * 100.0, 2),
                'median_posterior_rank': round(med_r, 1),
                'rank_95_ci_low': round(ci_low, 1),
                'rank_95_ci_high': round(ci_high, 1),
                'linguistic_governance_directive': ling_directive
            })
        return pd.DataFrame(post_audit)
        
    bat_post = simulate_posterior_details(conf_df[conf_df['role'] == 'Batter'].copy(), 'Batter')
    bowl_post = simulate_posterior_details(conf_df[conf_df['role'] == 'Bowler'].copy(), 'Bowler')
    
    comb_post = pd.concat([bat_post, bowl_post], ignore_index=True)
    out_post_path = os.path.join(AUDIT_DIR, "posterior_interpretation_audit.csv")
    comb_post.to_csv(out_post_path, index=False)
    print(f"\nExported Posterior Interpretation Audit Table to: {out_post_path}")
    
    print("\n=== POSTERIOR INTERPRETATION AUDIT SUMMARY ===")
    print(comb_post[['discipline', 'official_rank', 'player_name', 'official_cpri', 
                     'p_rank_1_pct', 'p_rank_le_5_pct', 'p_rank_le_10_pct', 
                     'median_posterior_rank', 'linguistic_governance_directive']].to_string(index=False))
    
    return jack_df, comb_post

if __name__ == "__main__":
    run_full_jackknife_and_posterior_audit()

