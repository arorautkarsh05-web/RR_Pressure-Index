# RR Pressure Index 2027: Mathematical & Statistical Methodology

---

## 1. Contextual Pressure Modeling

### 1.1 Batting Pressure ($\Psi_{\text{bat}}$)
Batting pressure represents situational resource depletion and chase strain.
- **First Innings:**
  $$\Psi_{\text{bat, inn1}} = \min(1.0, \; 0.45 \cdot \text{CollapseStrain} + 0.35 \cdot \text{DeathStrain} + 0.20 \cdot \text{ParDeficitStrain})$$
- **Second Innings:**
  $$\Psi_{\text{bat, inn2}} = \min(1.0, \; (0.40 \cdot \text{RateStrain} + 0.30 \cdot \text{WicketScarcity} + 0.30 \cdot (\text{RateStrain} \times \text{Urgency})) \cdot \text{TargetDifficulty})$$
- **High-Pressure Domain:** $\Psi_{\text{bat}} \ge 0.55$.

### 1.2 Bowling Execution Leverage ($\Lambda_{\text{bowl}}$)
Bowling leverage represents pre-delivery win-probability swing expectation.
- Out-of-match cross-validated logistic win-probability model:
  $$WP = \sigma(\beta_0 + \beta_1 \cdot \text{RRR} + \beta_2 \cdot \text{WicketsRemaining} + \beta_3 \cdot \text{BallsRemaining})$$
- Leverage index measures potential swing in $WP$:
  $$\Lambda_{\text{bowl}} \ge 0.50 \implies \text{High-Leverage Execution}$$

---

## 2. Clustered Empirical Bayes Formulation

### 2.1 Kish Design Effect & Effective Sample Size
$$deff = 1 + (\bar{m} - 1) \cdot \rho_{\text{ICC}}$$
$$N_{\text{eff}} = \frac{N}{deff}$$
Where:
- $\rho_{\text{ICC, bowl}} = 0.0159$
- $\rho_{\text{ICC, bat}} = 0.0182$
- Average cluster size capped at $\bar{m} \le 24.0$ for bowlers and $\bar{m} \le 15.0$ for batters.

### 2.2 Precision-Weighted Conjugate Normal Update
$$\text{prec}_0 = \frac{1}{\tau_0^2}, \quad \text{prec}_{\text{data}} = \frac{N_{\text{eff}}}{\sigma_{\text{within}}^2}, \quad \text{prec}_{\text{post}} = \text{prec}_0 + \text{prec}_{\text{data}}$$
$$\theta_{\text{Bayes}} = \frac{\mu_0 \cdot \text{prec}_0 + \bar{y} \cdot \text{prec}_{\text{data}}}{\text{prec}_{\text{post}}}$$
$$\sigma_{\text{post}} = \sqrt{\frac{1}{\text{prec}_{\text{post}}}}$$
$$95\% \text{ Credible Interval} = [\theta_{\text{Bayes}} - 1.96 \cdot \sigma_{\text{post}}, \; \theta_{\text{Bayes}} + 1.96 \cdot \sigma_{\text{post}}]$$

### 2.3 Beta-Binomial Conjugacy for Proportions
For Boundary%, Dot%, and Wicket%:
$$\alpha_{\text{post}} = \alpha_0 + k, \quad \beta_{\text{post}} = \beta_0 + (N - k)$$
$$p_{\text{Bayes}} = \frac{\alpha_{\text{post}}}{\alpha_{\text{post}} + \beta_{\text{post}}}$$
$$\text{CI}_{95\%} = [\text{Beta}^{-1}(0.025, \alpha_{\text{post}}, \beta_{\text{post}}), \; \text{Beta}^{-1}(0.975, \alpha_{\text{post}}, \beta_{\text{post}})]$$

---

## 3. Composite Pressure Reliability Index (CPRI)

$$\text{CPRI}_{\text{raw, bat}} = 0.40 \cdot Z_{\Delta\text{SR}} + 0.30 \cdot Z_{\text{Bnd\%}} - 0.15 \cdot Z_{\text{Dot\%}} - 0.15 \cdot Z_{\text{Dis\%}}$$
$$\text{CPRI}_{\text{raw, bowl}} = -0.40 \cdot Z_{\Delta\text{Econ}} - 0.30 \cdot Z_{\text{Bnd\%}} + 0.15 \cdot Z_{\text{Dot\%}} + 0.15 \cdot Z_{\text{Wkt\%}}$$
$$\text{CPRI} = 50.0 + 15.0 \cdot \text{CPRI}_{\text{raw}}$$
$$\text{SE}_{\text{CPRI}} = 15.0 \times 0.40 \times \left(\frac{\sigma_{\text{post}}}{\sigma_{\Delta}}\right)$$
