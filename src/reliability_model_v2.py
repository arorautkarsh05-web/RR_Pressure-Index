"""
RR PRESSURE INDEX 2027 — PHASE 02.1: RELIABILITY MODEL V2
Metric-Specific Bayesian Likelihoods & Contextual Index Modelling.

Key Features:
- Beta-Binomial Likelihood with Empirical Bayes Priors for Event Probabilities
  (Batting: Boundary%, Dot%, Dismissal%; Bowling: Conceded Boundary%, Dot%, Wicket%)
- Match-Clustered Normal-Normal Conjugate Model for Continuous Rates
  (Batting Strike Rate, Bowling Economy, Context-Adjusted Deltas)
- Intra-Cluster Correlation (ICC) and Design Effect sample size adjustment:
  n_eff = n / (1 + (m_bar - 1) * rho_ICC)
- 95% Bayesian Credible Intervals (lower, upper, width)
- Refined Decoupled Contextual Indices:
  * Chasing Clutch Index (CCI)
  * Collapse Recovery Index (CRI) / Collapse Pressure Index (CPI)
  * Death Execution Index (DEI)
- Empirical Proof of Contextual Independence
"""

import os
import pandas as pd
import numpy as np
from scipy.stats import beta, norm

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES_DIR = os.path.join(BASE_DIR, "outputs", "tables")
os.makedirs(TABLES_DIR, exist_ok=True)

def fit_beta_prior_mom(p_series, min_samples=30):
    """
    Fits Beta(alpha_0, beta_0) prior using Method of Moments on qualified peer proportions.
    """
    clean_p = p_series.dropna()
    clean_p = clean_p[(clean_p > 0.0) & (clean_p < 1.0)]
    
    if len(clean_p) < 10:
        return 5.0, 20.0, 25.0
        
    p_bar = clean_p.mean()
    s2 = clean_p.var()
    
    # Check theoretical bound: s2 < p_bar * (1 - p_bar)
    max_var = p_bar * (1.0 - p_bar)
    if s2 <= 0 or s2 >= max_var:
        M = float(min_samples)
    else:
        M = (max_var / s2) - 1.0
        M = np.clip(M, 15.0, 80.0)  # Bound empirical prior strength
        
    alpha_0 = p_bar * M
    beta_0 = (1.0 - p_bar) * M
    return float(alpha_0), float(beta_0), float(M)

def compute_icc(df_deliveries, group_col, outcome_col):
    """
    Computes Intra-Cluster Correlation (ICC) across matches.
    """
    df = df_deliveries[[group_col, outcome_col]].dropna()
    match_means = df.groupby(group_col)[outcome_col].agg(['count', 'mean'])
    grand_mean = df[outcome_col].mean()
    k = len(match_means)
    N = len(df)
    if k <= 1 or N <= k:
        return 0.02
        
    n_bar = N / float(k)
    msb = np.sum(match_means['count'] * (match_means['mean'] - grand_mean)**2) / (k - 1)
    
    ssw = df.groupby(group_col)[outcome_col].apply(lambda s: np.sum((s - s.mean())**2)).sum()
    msw = ssw / (N - k)
    
    s2_w = msw
    s2_a = max(0.0, (msb - msw) / n_bar)
    
    if (s2_a + s2_w) <= 0:
        return 0.02
    return float(np.clip(s2_a / (s2_a + s2_w), 0.005, 0.15))

def build_reliability_model_v2():
    print("=" * 80)
    print("RR PRESSURE INDEX 2027 — RELIABILITY MODEL V2: BAYESIAN HARDENING")
    print("=" * 80)

    # 1. Load Data
    print("\n[Step 1/5] Loading delivery feature store and context baselines...")
    features_path = os.path.join(TABLES_DIR, "delivery_pressure_features_v2.csv")
    baselines_path = os.path.join(TABLES_DIR, "context_adjusted_baselines.csv")
    
    df_del = pd.read_csv(features_path, low_memory=False)
    df_base = pd.read_csv(baselines_path)

    # 2. Compute Match Clustering ICC
    print("\n[Step 2/5] Calculating Intra-Cluster Correlation (ICC) across matches...")
    bat_press_del = df_del[df_del['is_bat_pressure'] & (df_del['extras_type'] != 'wide')]
    bowl_lev_del = df_del[df_del['is_bowl_leverage'] & df_del['is_legal']]

    bat_icc_runs = compute_icc(bat_press_del, 'match_id', 'runs')
    bowl_icc_runs = compute_icc(bowl_lev_del, 'match_id', 'bowler_runs_conceded')
    print(f"  Batting Pressure ICC (runs/ball): {bat_icc_runs:.4f}")
    print(f"  Bowling Leverage ICC (conceded runs/ball): {bowl_icc_runs:.4f}")

    # -------------------------------------------------------------
    # 3. BATTING BAYESIAN MODELLING
    # -------------------------------------------------------------
    print("\n[Step 3/5] Estimating Batting Bayesian Posteriors & Credible Intervals...")
    df_bat = df_base[df_base['role'] == 'batter'].copy()
    qual_bat = df_bat[df_bat['pressure_balls'] >= 30].copy()

    # Prior for Boundary%
    a_bnd, b_bnd, m_bnd = fit_beta_prior_mom(qual_bat['press_boundary_pct'])
    # Prior for Dot%
    a_dot, b_dot, m_dot = fit_beta_prior_mom(qual_bat['press_dot_pct'])
    # Prior for Dismissal%
    a_dis, b_dis, m_dis = fit_beta_prior_mom(qual_bat['press_dismissal_pct'])
    
    print(f"  Batting Boundary% Prior: Beta({a_bnd:.2f}, {b_bnd:.2f}) [M={m_bnd:.1f} balls]")
    print(f"  Batting Dot% Prior: Beta({a_dot:.2f}, {b_dot:.2f}) [M={m_dot:.1f} balls]")
    print(f"  Batting Dismissal% Prior: Beta({a_dis:.2f}, {b_dis:.2f}) [M={m_dis:.1f} balls]")

    # Prior for Strike Rate (Normal-Normal)
    mu_sr_0 = qual_bat['press_sr'].mean()
    s2_sr_0 = qual_bat['press_sr'].var()
    s2_sr_within = (bat_press_del['runs'] * 100.0).var()  # delivery level variance
    print(f"  Batting SR Population Prior: N({mu_sr_0:.1f}, {np.sqrt(s2_sr_0):.1f}^2)")

    # Compute posteriors for all batters
    bat_results = []
    for idx, row in df_bat.iterrows():
        n = row['pressure_balls']
        
        if n >= 5 and pd.notna(row['press_sr']):
            # Beta-Binomial: Boundary%
            k_bnd = round(row['press_boundary_pct'] * n)
            post_a_bnd = a_bnd + k_bnd
            post_b_bnd = b_bnd + (n - k_bnd)
            bayes_bnd_mean = post_a_bnd / (post_a_bnd + post_b_bnd)
            bnd_ci_low, bnd_ci_high = beta.ppf([0.025, 0.975], post_a_bnd, post_b_bnd)
            
            # Beta-Binomial: Dot%
            k_dot = round(row['press_dot_pct'] * n)
            post_a_dot = a_dot + k_dot
            post_b_dot = b_dot + (n - k_dot)
            bayes_dot_mean = post_a_dot / (post_a_dot + post_b_dot)
            dot_ci_low, dot_ci_high = beta.ppf([0.025, 0.975], post_a_dot, post_b_dot)

            # Beta-Binomial: Dismissal%
            k_dis = round(row['press_dismissal_pct'] * n)
            post_a_dis = a_dis + k_dis
            post_b_dis = b_dis + (n - k_dis)
            bayes_dis_mean = post_a_dis / (post_a_dis + post_b_dis)
            dis_ci_low, dis_ci_high = beta.ppf([0.025, 0.975], post_a_dis, post_b_dis)

            # Normal-Normal: Strike Rate with Cluster ICC Adjustment
            # Effective sample size: n_eff = n / (1 + (m_bar - 1) * rho)
            m_bar = min(15.0, max(1.0, n / 5.0))
            deff = 1.0 + (m_bar - 1.0) * bat_icc_runs
            n_eff = n / deff
            
            prec_0 = 1.0 / s2_sr_0
            prec_data = n_eff / s2_sr_within
            prec_post = prec_0 + prec_data
            
            bayes_sr_mean = ((mu_sr_0 * prec_0) + (row['press_sr'] * prec_data)) / prec_post
            bayes_sr_sd = np.sqrt(1.0 / prec_post)
            sr_ci_low = bayes_sr_mean - 1.96 * bayes_sr_sd
            sr_ci_high = bayes_sr_mean + 1.96 * bayes_sr_sd
            
            # Context-Adjusted Bayes Delta SR
            bayes_delta_context_sr = bayes_sr_mean - row['exp_sr']
        else:
            bayes_bnd_mean = a_bnd / (a_bnd + b_bnd)
            bnd_ci_low, bnd_ci_high = beta.ppf([0.025, 0.975], a_bnd, b_bnd)
            bayes_dot_mean = a_dot / (a_dot + b_dot)
            dot_ci_low, dot_ci_high = beta.ppf([0.025, 0.975], a_dot, b_dot)
            bayes_dis_mean = a_dis / (a_dis + b_dis)
            dis_ci_low, dis_ci_high = beta.ppf([0.025, 0.975], a_dis, b_dis)
            
            bayes_sr_mean = mu_sr_0
            bayes_sr_sd = np.sqrt(s2_sr_0)
            sr_ci_low = mu_sr_0 - 1.96 * bayes_sr_sd
            sr_ci_high = mu_sr_0 + 1.96 * bayes_sr_sd
            bayes_delta_context_sr = np.nan

        bat_results.append({
            'player_id': row['player_id'],
            'player_name': row['player_name'],
            'role': 'batter',
            'pressure_balls': n,
            'normal_balls': row['normal_balls'],
            # Empirical
            'raw_press_sr': row['press_sr'],
            'raw_press_boundary_pct': row['press_boundary_pct'],
            'raw_press_dot_pct': row['press_dot_pct'],
            'raw_press_dismissal_pct': row['press_dismissal_pct'],
            # Expected Context Benchmark
            'exp_sr': row['exp_sr'],
            'delta_context_sr': row['delta_context_sr'],
            'delta_raw_sr': row['delta_raw_sr'],
            'confounding_gap_sr': row['confounding_gap_sr'],
            # Bayesian Posterior & Uncertainty
            'bayes_press_sr': bayes_sr_mean,
            'bayes_press_sr_sd': bayes_sr_sd,
            'bayes_sr_ci_low': sr_ci_low,
            'bayes_sr_ci_high': sr_ci_high,
            'bayes_sr_ci_width': sr_ci_high - sr_ci_low,
            'bayes_delta_context_sr': bayes_delta_context_sr,
            
            'bayes_press_boundary_pct': bayes_bnd_mean,
            'bayes_bnd_ci_low': bnd_ci_low,
            'bayes_bnd_ci_high': bnd_ci_high,
            'bayes_bnd_ci_width': bnd_ci_high - bnd_ci_low,

            'bayes_press_dot_pct': bayes_dot_mean,
            'bayes_dot_ci_low': dot_ci_low,
            'bayes_dot_ci_high': dot_ci_high,
            'bayes_dot_ci_width': dot_ci_high - dot_ci_low,

            'bayes_press_dismissal_pct': bayes_dis_mean,
            'bayes_dis_ci_low': dis_ci_low,
            'bayes_dis_ci_high': dis_ci_high,
            'bayes_dis_ci_width': dis_ci_high - dis_ci_low,
        })
    df_bat_bayes = pd.DataFrame(bat_results)

    # -------------------------------------------------------------
    # 4. BOWLING BAYESIAN MODELLING
    # -------------------------------------------------------------
    print("\n[Step 4/5] Estimating Bowling Bayesian Posteriors & Credible Intervals...")
    df_bowl = df_base[df_base['role'] == 'bowler'].copy()
    qual_bowl = df_bowl[df_bowl['leverage_balls'] >= 40].copy()

    # Priors for Bowler Probabilities
    a_bbnd, b_bbnd, m_bbnd = fit_beta_prior_mom(qual_bowl['lev_boundary_pct'])
    a_bdot, b_bdot, m_bdot = fit_beta_prior_mom(qual_bowl['lev_dot_pct'])
    a_bwkt, b_bwkt, m_bwkt = fit_beta_prior_mom(qual_bowl['lev_wicket_pct'])

    print(f"  Bowling Boundary% Conceded Prior: Beta({a_bbnd:.2f}, {b_bbnd:.2f}) [M={m_bbnd:.1f} balls]")
    print(f"  Bowling Dot% Prior: Beta({a_bdot:.2f}, {b_bdot:.2f}) [M={m_bdot:.1f} balls]")
    print(f"  Bowling Wicket% Prior: Beta({a_bwkt:.2f}, {b_bwkt:.2f}) [M={m_bwkt:.1f} balls]")

    # Prior for Economy Rate (Normal-Normal)
    mu_econ_0 = qual_bowl['lev_econ'].mean()
    s2_econ_0 = qual_bowl['lev_econ'].var()
    s2_econ_within = (bowl_lev_del['bowler_runs_conceded'] * 6.0).var()
    print(f"  Bowling Economy Population Prior: N({mu_econ_0:.2f}, {np.sqrt(s2_econ_0):.2f}^2)")

    bowl_results = []
    for idx, row in df_bowl.iterrows():
        n = row['leverage_balls']
        
        if n >= 6 and pd.notna(row['lev_econ']):
            # Beta-Binomial: Boundary% Conceded
            k_bnd = round(row['lev_boundary_pct'] * n)
            post_a_bnd = a_bbnd + k_bnd
            post_b_bnd = b_bbnd + (n - k_bnd)
            bayes_bnd_mean = post_a_bnd / (post_a_bnd + post_b_bnd)
            bnd_ci_low, bnd_ci_high = beta.ppf([0.025, 0.975], post_a_bnd, post_b_bnd)

            # Beta-Binomial: Dot%
            k_dot = round(row['lev_dot_pct'] * n)
            post_a_dot = a_bdot + k_dot
            post_b_dot = b_bdot + (n - k_dot)
            bayes_dot_mean = post_a_dot / (post_a_dot + post_b_dot)
            dot_ci_low, dot_ci_high = beta.ppf([0.025, 0.975], post_a_dot, post_b_dot)

            # Beta-Binomial: Wicket%
            k_wkt = round(row['lev_wicket_pct'] * n)
            post_a_wkt = a_bwkt + k_wkt
            post_b_wkt = b_bwkt + (n - k_wkt)
            bayes_wkt_mean = post_a_wkt / (post_a_wkt + post_b_wkt)
            wkt_ci_low, wkt_ci_high = beta.ppf([0.025, 0.975], post_a_wkt, post_b_wkt)

            # Normal-Normal: Economy with Cluster ICC Adjustment
            m_bar = min(24.0, max(1.0, n / 4.0))
            deff = 1.0 + (m_bar - 1.0) * bowl_icc_runs
            n_eff = n / deff
            
            prec_0 = 1.0 / s2_econ_0
            prec_data = n_eff / s2_econ_within
            prec_post = prec_0 + prec_data
            
            bayes_econ_mean = ((mu_econ_0 * prec_0) + (row['lev_econ'] * prec_data)) / prec_post
            bayes_econ_sd = np.sqrt(1.0 / prec_post)
            econ_ci_low = bayes_econ_mean - 1.96 * bayes_econ_sd
            econ_ci_high = bayes_econ_mean + 1.96 * bayes_econ_sd
            
            # Context-Adjusted Bayes Delta Econ
            bayes_delta_context_econ = bayes_econ_mean - row['exp_econ']
        else:
            bayes_bnd_mean = a_bbnd / (a_bbnd + b_bbnd)
            bnd_ci_low, bnd_ci_high = beta.ppf([0.025, 0.975], a_bbnd, b_bbnd)
            bayes_dot_mean = a_bdot / (a_bdot + b_bdot)
            dot_ci_low, dot_ci_high = beta.ppf([0.025, 0.975], a_bdot, b_bdot)
            bayes_wkt_mean = a_bwkt / (a_bwkt + b_bwkt)
            wkt_ci_low, wkt_ci_high = beta.ppf([0.025, 0.975], a_bwkt, b_bwkt)
            
            bayes_econ_mean = mu_econ_0
            bayes_econ_sd = np.sqrt(s2_econ_0)
            econ_ci_low = mu_econ_0 - 1.96 * bayes_econ_sd
            econ_ci_high = mu_econ_0 + 1.96 * bayes_econ_sd
            bayes_delta_context_econ = np.nan

        bowl_results.append({
            'player_id': row['player_id'],
            'player_name': row['player_name'],
            'role': 'bowler',
            'pressure_balls': n,
            'normal_balls': row['normal_balls'],
            # Empirical
            'raw_press_econ': row['lev_econ'],
            'raw_press_boundary_pct': row['lev_boundary_pct'],
            'raw_press_dot_pct': row['lev_dot_pct'],
            'raw_press_wicket_pct': row['lev_wicket_pct'],
            # Expected Context Benchmark
            'exp_econ': row['exp_econ'],
            'delta_context_econ': row['delta_context_econ'],
            'delta_raw_econ': row['delta_raw_econ'],
            'confounding_gap_econ': row['confounding_gap_econ'],
            # Bayesian Posterior & Uncertainty
            'bayes_press_econ': bayes_econ_mean,
            'bayes_press_econ_sd': bayes_econ_sd,
            'bayes_econ_ci_low': econ_ci_low,
            'bayes_econ_ci_high': econ_ci_high,
            'bayes_econ_ci_width': econ_ci_high - econ_ci_low,
            'bayes_delta_context_econ': bayes_delta_context_econ,

            'bayes_press_boundary_pct': bayes_bnd_mean,
            'bayes_bnd_ci_low': bnd_ci_low,
            'bayes_bnd_ci_high': bnd_ci_high,
            'bayes_bnd_ci_width': bnd_ci_high - bnd_ci_low,

            'bayes_press_dot_pct': bayes_dot_mean,
            'bayes_dot_ci_low': dot_ci_low,
            'bayes_dot_ci_high': dot_ci_high,
            'bayes_dot_ci_width': dot_ci_high - dot_ci_low,

            'bayes_press_wicket_pct': bayes_wkt_mean,
            'bayes_wkt_ci_low': wkt_ci_low,
            'bayes_wkt_ci_high': wkt_ci_high,
            'bayes_wkt_ci_width': wkt_ci_high - wkt_ci_low,
        })
    df_bowl_bayes = pd.DataFrame(bowl_results)

    # Save Bayesian Model Comparison Table
    bayes_comp_df = pd.concat([df_bat_bayes, df_bowl_bayes], ignore_index=True)
    comp_path = os.path.join(TABLES_DIR, "bayesian_model_comparison.csv")
    bayes_comp_df.to_csv(comp_path, index=False)
    print(f"  Saved Bayesian Comparison Table ({len(bayes_comp_df)} records) to: {comp_path}")

    # -------------------------------------------------------------
    # 5. REFINED CONTEXTUAL INDICES & INDEPENDENCE PROOF
    # -------------------------------------------------------------
    print("\n[Step 5/5] Formulating Refined Contextual Indices & Testing Independence...")
    
    # Delivery subsets
    df_bat_legal = df_del[df_del['extras_type'] != 'wide'].copy()
    df_bowl_legal = df_del[df_del['is_legal']].copy()

    # A. Batting Contextual Indices:
    # 1. Chasing Clutch (CCI): Innings 2 pressure balls
    cci_bat = df_bat_legal[df_bat_legal['is_bat_chasing_clutch']].groupby('striker_id').agg(
        cci_balls=('innings_ball_num', 'count'),
        cci_runs=('runs', 'sum'),
        cci_wickets=('is_wicket', 'sum')
    ).reset_index()
    cci_bat['cci_sr'] = (cci_bat['cci_runs'] / cci_bat['cci_balls']) * 100.0

    # 2. Collapse Recovery (CRI): overs 1-12, wickets lost >= 3, collapse_strain >= 0.40
    cri_bat = df_bat_legal[df_bat_legal['is_collapse_crisis']].groupby('striker_id').agg(
        cri_balls=('innings_ball_num', 'count'),
        cri_runs=('runs', 'sum'),
        cri_wickets=('is_wicket', 'sum')
    ).reset_index()
    cri_bat['cri_sr'] = (cri_bat['cri_runs'] / cri_bat['cri_balls']) * 100.0

    # 3. Death Execution (DEI): overs 16-20 pressure balls
    dei_bat = df_bat_legal[df_bat_legal['is_death_overs'] & df_bat_legal['is_bat_pressure']].groupby('striker_id').agg(
        dei_balls=('innings_ball_num', 'count'),
        dei_runs=('runs', 'sum'),
        dei_wickets=('is_wicket', 'sum')
    ).reset_index()
    dei_bat['dei_sr'] = (dei_bat['dei_runs'] / dei_bat['dei_balls']) * 100.0

    # Merge Batting Indices
    ctx_bat = pd.merge(df_bat[['player_id', 'player_name', 'pressure_balls', 'delta_context_sr']], cci_bat, left_on='player_id', right_on='striker_id', how='left')
    ctx_bat = pd.merge(ctx_bat, cri_bat, left_on='player_id', right_on='striker_id', how='left')
    ctx_bat = pd.merge(ctx_bat, dei_bat, left_on='player_id', right_on='striker_id', how='left')

    # B. Bowling Contextual Indices:
    # 1. Chasing Clutch (CCI): Innings 2 bowling execution leverage
    cci_bowl = df_bowl_legal[df_bowl_legal['is_bowl_chasing_clutch']].groupby('bowler_id').agg(
        cci_balls=('innings_ball_num', 'count'),
        cci_runs=('bowler_runs_conceded', 'sum'),
        cci_wickets=('is_bowler_wicket', 'sum')
    ).reset_index()
    cci_bowl['cci_econ'] = (cci_bowl['cci_runs'] / cci_bowl['cci_balls']) * 6.0

    # 2. Collapse Pressure (CPI): overs 1-10 powerplay & collapse leverage
    cpi_bowl = df_bowl_legal[(df_bowl_legal['overid'] <= 10) & df_bowl_legal['is_bowl_leverage']].groupby('bowler_id').agg(
        cpi_balls=('innings_ball_num', 'count'),
        cpi_runs=('bowler_runs_conceded', 'sum'),
        cpi_wickets=('is_bowler_wicket', 'sum')
    ).reset_index()
    cpi_bowl['cpi_econ'] = (cpi_bowl['cpi_runs'] / cpi_bowl['cpi_balls']) * 6.0

    # 3. Death Execution (DEI): overs 16-20 bowling execution leverage
    dei_bowl = df_bowl_legal[df_bowl_legal['is_death_overs'] & df_bowl_legal['is_bowl_leverage']].groupby('bowler_id').agg(
        dei_balls=('innings_ball_num', 'count'),
        dei_runs=('bowler_runs_conceded', 'sum'),
        dei_wickets=('is_bowler_wicket', 'sum')
    ).reset_index()
    dei_bowl['dei_econ'] = (dei_bowl['dei_runs'] / dei_bowl['dei_balls']) * 6.0

    # Merge Bowling Indices
    ctx_bowl = pd.merge(df_bowl[['player_id', 'player_name', 'leverage_balls', 'delta_context_econ']], cci_bowl, left_on='player_id', right_on='bowler_id', how='left')
    ctx_bowl = pd.merge(ctx_bowl, cpi_bowl, left_on='player_id', right_on='bowler_id', how='left')
    ctx_bowl = pd.merge(ctx_bowl, dei_bowl, left_on='player_id', right_on='bowler_id', how='left')

    # Save Contextual Index Validation Table
    ctx_bat['role'] = 'batter'
    ctx_bowl['role'] = 'bowler'
    ctx_combined = pd.concat([ctx_bat, ctx_bowl], ignore_index=True)
    ctx_path = os.path.join(TABLES_DIR, "contextual_index_validation.csv")
    ctx_combined.to_csv(ctx_path, index=False)
    print(f"  Saved Contextual Index Validation Table to: {ctx_path}")

    # Compute and display correlation matrix for qualified batters
    q_bat_ctx = ctx_bat[(ctx_bat['cci_balls'] >= 15) & (ctx_bat['cri_balls'] >= 15) & (ctx_bat['dei_balls'] >= 15)]
    if len(q_bat_ctx) >= 10:
        bat_corr = q_bat_ctx[['cci_sr', 'cri_sr', 'dei_sr']].corr(method='spearman')
        print("\nBATTER CONTEXTUAL INDICES SPEARMAN CORRELATION MATRIX:")
        print(bat_corr.round(3))
        
    # Compute and display correlation matrix for qualified bowlers
    q_bowl_ctx = ctx_bowl[(ctx_bowl['cci_balls'] >= 20) & (ctx_bowl['cpi_balls'] >= 20) & (ctx_bowl['dei_balls'] >= 20)]
    if len(q_bowl_ctx) >= 10:
        bowl_corr = q_bowl_ctx[['cci_econ', 'cpi_econ', 'dei_econ']].corr(method='spearman')
        print("\nBOWLER CONTEXTUAL INDICES SPEARMAN CORRELATION MATRIX:")
        print(bowl_corr.round(3))

    print("=" * 80)
    return bayes_comp_df, ctx_combined

if __name__ == "__main__":
    build_reliability_model_v2()

