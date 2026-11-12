# RR Pressure Index 2027: Methodological Boundaries & Limitations

---

## 1. Distributional Assumptions (Normal-Normal Conjugacy)

- **Issue:** Strike rates and economy rates are strictly non-negative real numbers, whereas Gaussian distributions assign non-zero density to negative values.
- **Impact:** For qualified players ($N \ge 50$), posterior means are $>4\sigma$ from zero, making boundary truncation effects negligible in practice. However, unconstrained extrapolation to very small samples ($N < 20$) can produce negative credible bounds.
- **Recommended Evolution:** Transition rate metrics to Gamma-Poisson generalized linear mixed models (GLMM) or Log-Normal empirical Bayes models.

---

## 2. Homogeneous Intra-Cluster Correlation (ICC)

- **Issue:** The model applies a single global ICC estimate across all bowlers ($\rho = 0.0159$) and batters ($\rho = 0.0182$).
- **Impact:** Certain bowling styles (e.g., wrist spinners dependent on turn) exhibit higher match-to-match variance than control pacers. A uniform design effect slightly over-deflates effective sample sizes for ultra-consistent bowlers and under-deflates highly volatile performers.
- **Mitigation:** Empirical sensitivity testing confirms that varying ICC by 600% ($\rho \in [0.005, 0.035]$) shifts top player rankings by less than 0.1 rpo economy and preserves 100% Top 10 membership.

---

## 3. Epistemic Uncertainty in Small Samples (Tier B Classification)

- **Issue:** Players with moderate sample sizes (e.g. Phil Salt $N=55$, George Dockrell $N=76$, Naman Dhir $N=91$) display wider 95% Credible Intervals spanning 15–20 CPRI points.
- **Decision Rule for Franchise Bidding:** Franchise leadership should not treat Tier B CPRI point estimates as definitive guarantees. Bidding premiums should be discounted by the width of the lower credible bound (`cpri_ci_low`) to avoid overpaying for high-variance sample spikes.
