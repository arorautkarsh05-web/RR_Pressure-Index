# RR Pressure Index 2027: Comprehensive Data Dictionary

---

## 1. Feature Store: `outputs/tables/delivery_pressure_features_v2.csv`

| Column Name | Data Type | Description | Operational Boundary / Allowed Values |
| :--- | :---: | :--- | :--- |
| `match_id` | Integer | Unique identifier for match | 837 unique senior matches |
| `innings` | Integer | Innings number (1 or 2) | 1, 2 |
| `overid` | Integer | Over index in innings | 0 to 19 |
| `innings_ball_num` | Integer | Ball index within innings | 1 to 140+ |
| `striker_id` | Integer | Entity ID of batter facing delivery | Unique player identifier |
| `bowler_id` | Integer | Entity ID of bowler | Unique player identifier |
| `runs` | Integer | Runs scored directly off the bat | 0, 1, 2, 3, 4, 6 |
| `extras_type` | String | Extra category if illegal/extra delivery | `wide`, `Overstep`, `legbyes`, `byes`, `other`, `Penalty`, `NaN` |
| `is_legal` | Boolean | Legal delivery flag for bowling | True for balls excluding wide, overstep, other |
| `team_runs` | Integer | Total runs scored by team on delivery | `runs` + extra runs |
| `bowler_runs_conceded` | Integer | Runs charged against bowler's economy | `team_runs` excluding byes and leg-byes |
| `is_wicket` | Boolean | Wicket event occurred | True if batter dismissed |
| `is_bowler_wicket` | Boolean | Dismissal credited to bowler | True for Bowled, Caught, LBW, Stumped, Hit Wicket |
| `cum_runs_before` | Integer | Pre-delivery total team score | Strictly monotonically non-decreasing |
| `cum_wickets_before` | Integer | Pre-delivery total team wickets lost | 0 to 9 |
| `legal_balls_bowled` | Integer | Pre-delivery legal deliveries in innings | 0 to 119 |
| `balls_remaining` | Integer | Expected legal deliveries remaining | $120 - \text{legal\_balls\_bowled}$ |
| `wickets_remaining` | Integer | Remaining batting wickets | $10 - \text{cum\_wickets\_before}$ |
| `rrr` | Float | Required run rate (2nd innings only) | Runs required / (balls remaining / 6) |
| `psi_bat` | Float | Continuous Batting Pressure Index | $[0.0, 1.0]$ |
| `lambda_bowl` | Float | Continuous Bowling Leverage Index | $[0.0, 1.0]$ |
| `is_bat_pressure` | Boolean | High batting pressure domain | True if $\Psi_{\text{bat}} \ge 0.55$ |
| `is_bowl_leverage` | Boolean | High bowling leverage domain | True if $\Lambda_{\text{bowl}} \ge 0.50$ |

---

## 2. Rankings Tables: `outputs/rankings/top_10_*.csv`

| Column Name | Data Type | Description |
| :--- | :---: | :--- |
| `pressure_rank` | Integer | Official ranking position (1 to 10) |
| `player_id` | Integer | Unique player entity ID |
| `player_name` | String | Full name of player |
| `competitions` | String | Eligible competition tiers (e.g. `IPL/T20I`, `IPL`, `T20I`) |
| `matches` | Integer | Total matches played |
| `pressure_balls` | Float | Total pressure/leverage balls bowled or faced |
| `bayes_estimate_sr` / `econ` | Float | Conjugate empirical Bayes posterior mean |
| `ci_95_low` | Float | Lower bound of 95% Bayesian Credible Interval |
| `ci_95_high` | Float | Upper bound of 95% Bayesian Credible Interval |
| `ci_95_width` | Float | Credible interval width ($\text{High} - \text{Low}$) |
| `confidence_class` | String | Confidence classification (`Tier A`: $N \ge 100$, `Tier B`: $50 \le N < 100$) |
| `CPRI` | Float | Composite Pressure Reliability Index (0–100 scale, mean 50, SD 15) |
| `cpri_ci_low` | Float | Lower 95% credible bound for CPRI |
| `cpri_ci_high` | Float | Upper 95% credible bound for CPRI |
| `ranking_explanation` | String | Narrative analytical scouting justification |
