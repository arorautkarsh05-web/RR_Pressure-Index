# RR PRESSURE INDEX 2027 — Analytical Feasibility & Pressure Modeling Foundations
## SupeRR Selector Season 2 — Mathematical Derivations & Cricketing Context Specification

**Prepared by:** Senior Sports Statistician, Lead Cricket Data Scientist & Senior IPL Auction Strategist  
**Scope:** Senior IPL & T20I (2022–2026)  
**Status:** Phase 01 Validated  

---

### Table of Contents
1. [Executive Summary & Analytical Principles](#1-executive-summary--analytical-principles)
2. [Variable Availability Audit (Direct vs Derived)](#2-variable-availability-audit-direct-vs-derived)
3. [Mathematical Formulation of Derived Context Features](#3-mathematical-formulation-of-derived-context-features)
4. [Innings 2 Chase Pressure Architecture](#4-innings-2-chase-pressure-architecture)
5. [Innings 1 Baseline & Par Score Pressure Architecture](#5-innings-1-baseline--par-score-pressure-architecture)
6. [Bowling Leverage & Contextual Execution](#6-bowling-leverage--contextual-execution)
7. [Rain Interventions (DLS) & Super Over Treatment](#7-rain-interventions-dls--super-over-treatment)
8. [Data Gaps, Constraints & Phase 02 Recommendations](#8-data-gaps-constraints--phase-02-recommendations)

---

### 1. Executive Summary & Analytical Principles

In elite franchise cricket, assessing player reliability under pressure requires separating genuine clutch execution from superficial statistical volume. A batter scoring 60 off 40 in a blowout first innings faces fundamentally different psychological and tactical constraints than a batter scoring 28 off 14 chasing 11.5 RRR with 4 wickets remaining. Similarly, a bowler defending 12 runs in the 20th over operates under vastly higher leverage than a bowler bowling in the 12th over of a non-competitive fixture.

#### Franchise Analytical Principles:
1. **Context-Normalized Baselines**: Player performance under pressure must be evaluated against their own neutral baseline, not across uncalibrated raw aggregates.
2. **Inherent Asymmetry Between Innings**: Required Run Rate (RRR) does not exist in the first innings. First-innings pressure must be derived from resource depletion (wickets lost vs overs left) and par-score velocity, whereas second-innings pressure is dictated by the chase equation.
3. **Sample Size & Uncertainty Penalties**: A player with 15 clutch deliveries and a 250 strike rate cannot be ranked above a player with 350 clutch deliveries at 170 strike rate without Bayesian shrinkage and uncertainty modeling.
4. **Repeatability Over Outliers**: Single-match heroics must not dominate multi-year dependability.

---

### 2. Variable Availability Audit (Direct vs Derived)

| Variable Class | Feature Name | Direct vs Derived | Source Column(s) / Formula | Status in Raw Data |
| :--- | :--- | :---: | :--- | :--- |
| **Batting** | Striker Runs | **Direct** | `runs` | Available on every delivery. |
| **Batting** | Boundaries (4s / 6s) | **Direct** | `is_four`, `is_six` | Available on every delivery. |
| **Batting** | Realized Batting Position | **Direct** | `batting_order` | Available in `ball_by_ball.csv`. |
| **Batting** | Dismissal Type | **Direct** | `dismissal_type` | Available when `is_wicket == True`. |
| **Batting** | Innings Phase | **Derived** | `overid` $\le 6 \implies$ PP; $7-15 \implies$ Mid; $16-20 \implies$ Death | Directly computable. |
| **Batting** | Current Team Score | **Derived** | Cumulative sum of $\text{team\_runs}$ | Computable via derived ball runs. |
| **Batting** | Wickets Remaining | **Derived** | $10 - \text{cumsum}(\text{is\_wicket})$ | Computable on every delivery. |
| **Batting** | Balls Remaining | **Derived** | $120 - \text{cumsum}(\text{is\_legal})$ | Computable with revised over bounds. |
| **Batting** | Target | **Derived** | $\text{revised\_target}$ or $(\text{Inn1\_Score} + 1)$ | Derived from Inn 1 or `matches.csv`. |
| **Batting** | Required Run Rate (RRR) | **Derived** | $(\text{Runs Required} / \text{Balls Remaining}) \times 6$ | Derived for Innings 2. |
| **Batting** | Current Run Rate (CRR) | **Derived** | $(\text{Current Score} / \text{Legal Balls Bowled}) \times 6$ | Derived for both innings. |
| **Bowling** | Bowler Deliveries | **Direct** | Delivery row count per `bowler_id` | Available on every delivery. |
| **Bowling** | Bowler Legal Balls | **Derived** | $\mathbf{1}_{\{\text{extras\_type} \notin [\text{'wide'}, \text{'Overstep'}, \text{'other'}]\}}$ | Derived delivery-level flag. |
| **Bowling** | Bowler Runs Conceded | **Derived** | $\text{runs} + \mathbf{1}_{\text{wide}} + \mathbf{1}_{\text{no-ball}} + \text{extras\_2\_runs}$ | Byes/legbyes excluded from bowler. |
| **Bowling** | Bowler Wickets | **Derived** | $\text{is\_wicket} \land (\text{dismissal} \notin [\text{RunOut}, \text{Retire Out}])$ | Excludes team-only dismissals. |
| **Bowling** | Dot Balls Bowled | **Derived** | $\mathbf{1}_{\{\text{bowler\_runs\_conceded} = 0\}}$ | Directly computable per ball. |
| **Bowling** | Boundaries Conceded | **Derived** | $\mathbf{1}_{\{\text{is\_four} \lor \text{is\_six}\}}$ | Directly computable per ball. |
| **Bowling** | Defending / Death Over Leverage | **Derived** | RRR, wickets in hand, and balls remaining | Dynamically evaluated per ball. |

---

### 3. Mathematical Formulation of Derived Context Features

Let delivery $i$ occur in match $m$, innings $k \in \{1, 2\}$, at over $o \in \{1, \dots, 20\}$ and sequential ball $b$.

#### 3.1 Ball Legality Indicator
A ball is legal if and only if it is not a wide or no-ball:
$$\text{is\_legal}_i = \begin{cases} 1, & \text{if } \text{extras\_type}_i \notin \{\text{'wide'}, \text{'Overstep'}, \text{'other'}\} \\ 0, & \text{otherwise} \end{cases}$$

#### 3.2 Total Team Runs per Delivery
$$\text{team\_runs}_i = \text{runs}_i + \mathbf{1}_{\{\text{extras\_type}_i = \text{'wide'}\}} + \mathbf{1}_{\{\text{extras\_type}_i \in [\text{'Overstep'}, \text{'other'}]\}} + \text{extras\_2\_runs}_i$$

#### 3.3 Bowler Runs Conceded per Delivery
Byes and leg-byes are fielding extras and do not penalize the bowler:
$$\text{bowler\_runs}_i = \text{runs}_i + \mathbf{1}_{\{\text{extras\_type}_i = \text{'wide'}\}} + \mathbf{1}_{\{\text{extras\_type}_i \in [\text{'Overstep'}, \text{'other'}]\}} + \text{extras\_2\_runs}_i$$

#### 3.4 Innings Cumulative State
At delivery $i$, prior to its outcome:
$$\text{cum\_runs}_i = \sum_{j < i} \text{team\_runs}_j$$
$$\text{cum\_wickets}_i = \sum_{j < i} \mathbf{1}_{\{\text{is\_wicket}_j = \text{True}\}}$$
$$\text{wickets\_remaining}_i = 10 - \text{cum\_wickets}_i$$
$$\text{legal\_balls\_bowled}_i = \sum_{j < i} \text{is\_legal}_j$$
$$\text{balls\_remaining}_i = \max\left(0, N_{\text{total\_balls}} - \text{legal\_balls\_bowled}_i\right)$$
where $N_{\text{total\_balls}} = 120$ for regulation matches, or $\text{revised\_overs} \times 6$ for rain-truncated matches.

---

### 4. Innings 2 Chase Pressure Architecture

In the second innings, match pressure is explicitly defined by the chase equation:

#### 4.1 Target Definition
$$\text{Target}_m = \begin{cases} \text{revised\_target}_m, & \text{if } \text{revised\_target}_m \text{ is not null} \\ \text{Inn1\_Total}_m + 1, & \text{otherwise} \end{cases}$$

#### 4.2 Runs Required & Required Run Rate (RRR)
$$\text{runs\_required}_i = \max\left(0, \text{Target}_m - \text{cum\_runs}_i\right)$$
$$\text{RRR}_i = \begin{cases} \left(\frac{\text{runs\_required}_i}{\text{balls\_remaining}_i}\right) \times 6, & \text{if } \text{balls\_remaining}_i > 0 \\ 0, & \text{if } \text{runs\_required}_i = 0 \text{ (match won)} \\ \infty, & \text{if } \text{balls\_remaining}_i = 0 \land \text{runs\_required}_i > 0 \end{cases}$$

#### 4.3 Second-Innings Pressure Index ($\Psi_{2, i}$)
The situational pressure on delivery $i$ in a chase is a function of:
1. **Rate Stress Ratio**: $\rho_{\text{rate}} = \frac{\text{RRR}_i}{\text{Par\_RRR}}$ (where $\text{Par\_RRR} \approx 8.5$ runs/over in modern T20).
2. **Resource Scarcity (Wicket Depletion)**: $W_{\text{scarcity}} = \frac{10}{\text{wickets\_remaining}_i}$.
3. **Temporal Horizon (Balls Left)**: High RRR in over 19 (6 balls left) creates extreme binary leverage compared to over 8.

$$\Psi_{2, i} = f\left(\text{RRR}_i, \text{wickets\_remaining}_i, \text{balls\_remaining}_i\right) = \left(\frac{\text{RRR}_i}{8.5}\right)^{\alpha} \times \left(\frac{10}{\text{wickets\_remaining}_i + 1}\right)^{\beta} \times \left(\frac{120}{\text{balls\_remaining}_i + 12}\right)^{\gamma}$$

---

### 5. Innings 1 Baseline & Par Score Pressure Architecture

**Crucial Domain Insight:** The concept of Required Run Rate is mathematically undefined in Innings 1. Imposing an artificial RRR in the first innings violates fundamental cricket analytics principles.

Instead, first-innings pressure manifests through three distinct physical mechanisms:

#### 5.1 Collapse Recovery (Resource Crisis)
When top-order wickets fall rapidly, the batting side loses the option to play aggressively without risking being bowled out before the 20th over.
$$\text{Collapse\_Index}_i = \frac{10 - \text{wickets\_remaining}_i}{\max(1, \text{overid}_i)}$$
- *Example:* 24/3 after 4 overs $\implies$ Collapse Index = $3 / 4 = 0.75$ (Extreme Pressure: Batter must rebuild while maintaining minimum scoring velocity).
- *Example:* 120/2 after 14 overs $\implies$ Collapse Index = $2 / 14 = 0.14$ (Low Pressure: Batting side possesses abundant resources).

#### 5.2 Par Velocity Deficit
Comparing the actual score progression against the venue/competition historical expected par curve $\hat{S}(\text{over}, \text{wickets})$:
$$\Delta_{\text{par}, i} = \hat{S}(\text{over}_i, \text{wickets}_i) - \text{cum\_runs}_i$$
If the team is tracking 20 runs below par entering over 14, pressure intensifies to accelerate.

#### 5.3 Death Overs Acceleration Constraint (Overs 16–20)
In overs 16–20 of the first innings, the baseline expected scoring rate rises to 10.5–12.0 runs/over. Batters face maximum pressure to hit immediate boundaries against premier death bowlers with fielders spread to boundary ropes.

---

### 6. Bowling Leverage & Contextual Execution

Bowlers face peak pressure under symmetrical constraints to batters:
1. **Defending Low Targets / Tight Death Overs**: Bowling overs 18–20 with $\text{RRR} < 9.0$ and multiple wickets in hand.
2. **Breaking Critical Partnerships**: Bowling when batting opposition is accelerating ahead of par.
3. **Powerplay Containment**: Bowling overs 1–6 with only 2 fielders outside the 30-yard ring against aggressive openers.

#### Key Bowling Execution Metrics under High Leverage:
- **Dot Ball Frequency under Pressure**: $\text{Dot}\%_{\text{pressure}} = \frac{\text{Dots Bowled in High Leverage}}{\text{Total High-Leverage Deliveries Bowled}}$
- **Boundary Suppression Ratio**: $\text{Bnd}\%_{\text{pressure}} = \frac{\text{Boundaries Conceded in High Leverage}}{\text{Total High-Leverage Deliveries Bowled}}$
- **Clutch Wicket Rate**: High-leverage wickets taken per 100 high-leverage deliveries.
- **Economy Rate Delta**: $\Delta_{\text{Econ}} = \text{Econ}_{\text{Pressure}} - \text{Econ}_{\text{Baseline}}$ (A negative $\Delta_{\text{Econ}}$ indicates a bowler who restricts scoring *more* under pressure than their average baseline).

---

### 7. Rain Interventions (DLS) & Super Over Treatment

#### 7.1 DLS Matches (23 Matches Identified)
In rain-truncated matches, `matches.csv` populates:
- `first_inn_revised_overs`
- `second_inn_revised_overs`
- `revised_target`

**Rule:** When `revised_target` is present, the chase model must strictly utilize $\text{Target} = \text{revised\_target}$ and $\text{total\_balls} = \text{second\_inn\_revised\_overs} \times 6$. Using the raw Innings 1 score in a DLS match would invalidate the required run rate.

#### 7.2 Super Overs (6 Matches, 38 Deliveries Identified)
Super Overs (Innings 3 and 4) represent the ultimate expression of single-over clutch execution (e.g. DC vs RR IPL 2025 Match 40725, KKR vs RR IPL 2026 Match 50359).
- **Treatment:** Super over deliveries must be flagged with `is_super_over = True`.
- Because sample size in super overs is small (1–6 balls per player), super over performance must be used as a qualitative validation benchmark and leverage multiplier rather than distorting baseline sample counts.

---

### 8. Data Gaps, Constraints & Phase 02 Recommendations

#### Confirmed Forensic Data Constraints:
1. **Discrete Bye/Legbye Run Tally Absent**: `runs` is 0 on byes and legbyes; while 1 run is typically taken, multi-run byes or overthrows are not explicitly partitioned. Team totals reconcile within 1–2 runs of official totals.
2. **Fielding Trajectory Missing**: While stroke name, delivery style, speed, and pitch sector are available, fielder identity and dropped catches are not tracked.
3. **Pre-match Batting Order Nulls**: 30.58% nulls in `playing_eleven.csv`. *Solution:* Realized batting position is 100% complete in `ball_by_ball.csv` and will be used as the ground truth.

#### Recommendations for Phase 02 (Pressure Index Architecture):
1. **Unified Win Probability / Leverage Index Framework**: Adapt the concept of Leverage Index ($LI$) from baseball sabermetrics to T20 cricket, weighting every delivery by how much the outcome shifts the win probability.
2. **Empirical Bayesian Shrinkage**: For players with moderate sample size (100–250 balls), shrink pressure performance toward population priors to prevent small-sample distortion.
3. **Dual Ranking Architecture**: Generate distinct Top 10 Batters and Top 10 Bowlers rankings with full auditability, sample size confidence intervals, and explanatory diagnostic scorecards.

