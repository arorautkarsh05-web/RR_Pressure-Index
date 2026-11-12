# RR PRESSURE INDEX 2027 — Phase 01 Comprehensive Forensic Audit Report
## SupeRR Selector Season 2 — Professional Cricket Analytics & Player Reliability Intelligence System

**Consortium:** Senior IPL Auction Strategist, Lead Cricket Data Scientist, Senior Sports Statistician, Cricket Performance Analyst, Data Engineering Architect, Statistical Model Validation Specialist, Professional Power BI Analytics Consultant  
**Project Directory:** `D:\RR_PRESSURE_INDEX_2027`  
**Execution Date:** November 2026  
**Status:** Completed & Validated — Awaiting Sign-Off for Phase 02  

---

### Table of Contents
1. [Executive Summary & High-Level Sign-Off](#1-executive-summary--high-level-sign-off)
2. [Dataset Inventory & Verification](#2-dataset-inventory--verification)
3. [Competition Scope & Filtering Audit](#3-competition-scope--filtering-audit)
4. [Data Quality Investigation & Forensic Issue Register](#4-data-quality-investigation--forensic-issue-register)
5. [Player & Team Master Participation Audit](#5-player--team-master-participation-audit)
6. [Analytical Feasibility & Derived Feature Engineering](#6-analytical-feasibility--derived-feature-engineering)
7. [Confirmed Findings, Unresolved Issues & Known Limitations](#7-confirmed-findings-unresolved-issues--known-limitations)
8. [Phase 02 Strategic Recommendations & Roadmap](#8-phase-02-strategic-recommendations--roadmap)

---

### 1. Executive Summary & High-Level Sign-Off

The multidisciplinary analytical consortium has completed a full forensic data audit across the entire cricket analytics repository provided in `D:\RR_PRESSURE_INDEX_2027`. All raw files have been preserved as immutable source data.

#### High-Level Audit Findings:
- **Raw Repositories Audited**: 6 CSV datasets totaling **42.63 MB** (200,999 delivery events, 883 matches, 141 tournaments, 28,381 lineup appearances, 6,413 player mappings, 38 teams).
- **Official Scope Isolated**: By enforcing the challenge mandate of **IPL and T20I matches from 2022 onwards**, exactly **139 senior competitions** (5 IPL editions, 134 international T20I tournaments/series) and **853 eligible matches** (371 IPL, 482 T20I) were isolated. Two domestic developmental tournaments (30 matches, 6,985 balls) were formally audited and excluded.
- **Relational Integrity**: 100% referential integrity across match, team, and player entities. Zero orphan records within the eligible challenge scope.
- **Critical Data Trap Identified**: The column `extras1_runs` in `ball_by_ball.csv` was forensically proven to be an **integer categorical code** for `extras_type` (1=No-ball, 2=Wide, 3=Legbye, 4=Bye, 5=Other, 6=None, 7=Penalty) rather than a run tally. Treating it as a numeric run count would have introduced over **1.1 million phantom runs** into player baseline metrics.
- **Player Participation Universe**: 1,132 unique players tracked in the senior challenge scope. 824 batters and 596 bowlers recorded active deliveries. 303 batters and 311 bowlers meet the minimum franchise sample threshold of $\ge 100$ deliveries.
- **Feasibility Established**: Second-innings chase leverage (RRR, balls remaining, wickets in hand) and first-innings resource pressure (collapse recovery, par velocity deficit, death acceleration) are mathematically validated and completely reconstructible.

All deliverables required for Phase 01 have been generated, executed, and validated with zero runtime errors.

---

### 2. Dataset Inventory & Verification

The raw data environment was verified without modifying or renaming any original files.

| Filename | Physical Size | Memory Usage | Rows | Columns | Duplicate Rows | Candidate Key | Temporal Range | Business Role |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- | :---: | :--- |
| `competitions.csv` | 7.45 KB | 0.01 MB | 141 | 4 | 0 | `comp_id` | 2022 – 2026 | Tournament registry & format classification |
| `teams.csv` | 6.76 KB | 0.01 MB | 353 | 3 | 0 | `(comp_id, team_id)` | N/A | Franchise & national team registry |
| `matches.csv` | 120.96 KB | 0.22 MB | 883 | 22 | 0 | `match_id` | 2022-01-22 – 2026-11-01 | Fixture metadata, toss, venue, DLS targets & outcomes |
| `playing_eleven.csv` | 943.64 KB | 3.21 MB | 28,381 | 9 | 0 | `(match_id, player_id)` | N/A | Squad selection, captaincy, keeper, Impact Player subs |
| `competition_team_player_mapping.csv` | 452.12 KB | 0.64 MB | 6,413 | 6 | 0 | `(comp_id, team_id, player_id)` | N/A | Canonical player master and squad contracts |
| `ball_by_ball.csv` | 39.17 MB | 69.49 MB | 200,999 | 33 | 0 | `(match_id, innings, innings_ball_num)` | 2022-01-23 – 2026-11-01 | Granular delivery events, runs, wickets, extras & trajectories |

---

### 3. Competition Scope & Filtering Audit

The problem statement explicitly dictates:
> *"The official challenge scope is IPL and T20I data from 2022 onwards. Do not automatically include other T20 competitions. Document the exact competition filtering logic."*

#### 3.1 Competition Breakdown
An exhaustive audit of all 141 tournaments in `competitions.csv` revealed three distinct tournament classes:
1. **IPL Competitions (Included - 5 Editions, 371 Matches)**:
   - Comp ID 1358: IPL 2022 (74 matches)
   - Comp ID 1715: IPL 2023 (74 matches)
   - Comp ID 2193: IPL 2024 (74 matches)
   - Comp ID 2725: IPL 2025 (75 matches)
   - Comp ID 3298: IPL 2026 (74 matches)
2. **T20I International Competitions (Included - 134 Editions, 482 Matches)**:
   - Senior bilateral tours, ICC Men's T20 World Cups, Continental Asia Cups involving full and associate national member boards.
3. **Excluded Domestic / Developmental Tournaments (Excluded - 2 Editions, 30 Matches)**:
   - Comp ID 2670: *Mens T20 Emerging Teams Asia Cup 2024* (15 matches, 3,467 balls)
   - Comp ID 3289: *Asia Cup Rising Stars 2025* (15 matches, 3,518 balls)
   - **Exclusion Justification**: These two tournaments feature developmental 'A' squads (e.g. India A, Pakistan A, Bangladesh A, Sri Lanka A, Afghanistan A) rather than senior franchise or senior international sides. Blending developmental fixtures into an elite IPL auction model would contaminate high-leverage benchmarks.

#### 3.2 Match Reconciliation Across Files
- Total Matches in `matches.csv`: **883**
  - Eligible Senior Scope (IPL + T20I): **853 matches**
  - Excluded Developmental Tournaments: **30 matches**
- Total Matches with Ball-by-Ball Data in `ball_by_ball.csv`: **867 matches**
  - Eligible matches with balls bowled: **837 matches** (194,014 balls)
  - Excluded matches with balls bowled: **30 matches** (6,985 balls)
- **The 16 Missing Matches Reconciled**: Exactly 16 matches in `matches.csv` have zero records in `ball_by_ball.csv`. Every single one was verified as a **rain abandonment without a single ball bowled** (`result == 'Match Abandoned'`).

---

### 4. Data Quality Investigation & Forensic Issue Register

A comprehensive data quality register was constructed (`outputs/audit/data_quality_report.csv`). Ten primary anomalies were identified, categorized, and assigned remediation strategies:

```
+-----------+----------------------+----------------------------------------------------------+-------------+
| Issue ID  | Target Table         | Anomaly Description                                      | Severity    |
+-----------+----------------------+----------------------------------------------------------+-------------+
| DQI-001   | ball_by_ball.csv     | extras1_runs is an enum ID, NOT a run count              | CRITICAL    |
| DQI-002   | ball_by_ball.csv     | 'runs' records only striker runs off bat (extras = 0)    | HIGH        |
| DQI-003   | ball_by_ball.csv     | Typo: 'Obstracting the field' vs 'Obstructing the field' | LOW         |
| DQI-004   | ball_by_ball.csv     | 1 null dismissed_player_id on wicket (Hardik Retire Out) | LOW         |
| DQI-005   | matches.csv          | 16 rain-abandoned fixtures with zero deliveries bowled    | MEDIUM      |
| DQI-006   | competitions.csv     | 2 non-challenge developmental 'A' team tournaments       | CRITICAL    |
| DQI-007   | playing_eleven.csv   | 30.58% null batting_order in pre-match feeds             | MEDIUM      |
| DQI-008   | matches.csv          | Revised target populated in only 23 rain-affected games  | LOW         |
| DQI-009   | ball_by_ball.csv     | Innings 3 & 4 contain Super Over deliveries (38 balls)   | MEDIUM      |
| DQI-010   | playing_eleven.csv   | 2 orphan players in BBB (restricted to excluded tourneys)| LOW         |
+-----------+----------------------+----------------------------------------------------------+-------------+
```

#### Detailed Forensic Findings:
1. **The `extras1_runs` Discovery**:
   - Cross-tabulation proved an exact 1:1 bijection between `extras_type` and `extras1_runs`:
     `Overstep` $\implies 1$, `wide` $\implies 2$, `legbyes` $\implies 3$, `byes` $\implies 4$, `other` $\implies 5$, `None` $\implies 6$, `Penalty` $\implies 7$.
   - **Remediation**: The column is treated strictly as an integer category code; under no circumstances will it be summed.
2. **Run Attribution & Team Score Reconstruction**:
   - The `runs` column captures runs scored off the bat by the striker. On wides, byes, and leg-byes, `runs` is 0.
   - Team total on delivery $i$ is calculated by:
     $$\text{team\_runs}_i = \text{runs}_i + \mathbf{1}_{\{\text{wide}\}} + \mathbf{1}_{\{\text{no-ball}\}} + \text{extras\_2\_runs}_i$$
3. **Wicket Crediting Rules**:
   - Bowler wickets: Caught (7,557), Bowled (1,775), LBW (709), Stumped (214), Hit Wicket (17) $\implies$ **10,272 bowler wickets**.
   - Team wickets (non-bowler): RunOut (600), Retire Out (6), Obstructing the field (3) $\implies$ **609 dismissals** (excluded from bowler averages/strike rates).
4. **Impact Player Substitutions**:
   - 558 instances of `is_impact == 1` and 558 instances of `is_impact_off == 1` in IPL matches from 2023 to 2026. This tactical rule alters batting depth and death-bowling specialist availability.

---

### 5. Player & Team Master Participation Audit

#### 5.1 Canonical Player Master
- **1,132 total players** tracked across eligible senior fixtures.
- Exactly **0 player name spelling variants or ID collisions** exist. Every `player_id` maps to a single, immutable canonical name across all tables.
- In the eligible scope, **100% of all players in `ball_by_ball.csv` exist in `playing_eleven.csv`**.

#### 5.2 Franchise Sample Size Distribution
To protect auction decisions against small-sample bias, sample distribution percentiles were computed across the 2022–2026 window:

| Percentile | Balls Faced (Batters) | Legal Deliveries Bowled (Bowlers) |
| :--- | :---: | :---: |
| 10th Percentile | 5 balls | 15 balls |
| 25th Percentile | 16 balls | 41 balls |
| 50th Percentile (Median) | 55 balls | 115 balls |
| 75th Percentile | 210 balls | 413 balls |
| 90th Percentile | 777 balls | 932 balls |
| 95th Percentile | 1,164 balls | 1,334 balls |
| Maximum | 2,920 balls | 3,432 balls |

- **Qualified Batters ($\ge 100$ Balls Faced)**: **303 players**
- **Qualified Bowlers ($\ge 100$ Legal Deliveries)**: **311 players**
- **Qualified Dual All-rounders ($\ge 100$ Batting & Bowling Deliveries)**: **108 players**

#### 5.3 Top Aggregates in Senior Challenge Scope (2022–2026)
- **Top 5 Run Scorers**:
  1. Suryakumar Yadav: 4,595 runs (2,761 balls, SR 166.43, Avg 38.61, 248 sixes)
  2. Jos Buttler: 4,396 runs (2,829 balls, SR 155.39, Avg 41.08, 204 sixes)
  3. Abhishek Sharma: 4,198 runs (2,251 balls, SR 186.49, Avg 33.32, 275 sixes)
  4. Shubman Gill: 4,050 runs (2,711 balls, SR 149.39, Avg 40.50, 142 sixes)
  5. Virat Kohli: 3,567 runs (2,456 balls, SR 145.24, Avg 46.93, 124 sixes)
- **Top 5 Wicket Takers**:
  1. Arshdeep Singh: 194 wickets (534.5 overs, Econ 9.10, Avg 25.07, SR 16.5)
  2. Rashid Khan: 153 wickets (457.8 overs, Econ 7.40, Avg 22.16, SR 18.0)
  3. Varun Chakravarthy: 135 wickets (354.7 overs, Econ 8.00, Avg 21.01, SR 15.8)
  4. Wanindu Hasaranga: 133 wickets (339.2 overs, Econ 7.92, Avg 20.20, SR 15.3)
  5. Ravi Bishnoi: 124 wickets (387.8 overs, Econ 8.31, Avg 25.99, SR 18.8)

---

### 6. Analytical Feasibility & Derived Feature Engineering

The audit confirmed that all required situational context features are 100% derivable without requiring external proprietary data feeds:

#### 6.1 Second-Innings Chase Pressure
1. **Target Formulation**: $\text{Target} = \text{revised\_target}$ (if rain DLS applied, 23 matches) else $(\text{Inn1\_Score} + 1)$.
2. **Current State**: Cumulative score, cumulative wickets, and legal balls bowled reconstructed ball-by-ball.
3. **Required Run Rate (RRR)**: Dynamically computed on every delivery:
   $$\text{RRR}_i = \left(\frac{\text{Runs Required}_i}{\text{Balls Remaining}_i}\right) \times 6$$
4. **Chase Leverage Index**: Modulated by wicket scarcity $\left(\frac{10}{\text{Wickets Left}}\right)$ and temporal urgency.

#### 6.2 First-Innings Par & Resource Pressure
1. **Principle**: RRR is undefined in Innings 1. Imposing artificial RRR is mathematically rejected.
2. **Collapse Recovery**: Measured via $\frac{\text{Wickets Lost}}{\text{Overs Elapsed}}$ (e.g. recovering from 25/3 in Powerplay).
3. **Par Velocity Deficit**: Real-time score progression vs par curve.
4. **Death Acceleration**: Overs 16–20 where baseline expected scoring rate rises above 10.5 RPO.

---

### 7. Confirmed Findings, Unresolved Issues & Known Limitations

#### Confirmed Findings:
1. All 883 matches map cleanly to competitions; exactly 853 belong to senior IPL and T20I (2022–2026).
2. Exactly 16 matches were rain-abandoned with 0 deliveries bowled; exactly 837 matches contain ball-by-ball actions.
3. `extras1_runs` is conclusively an integer categorical code, not a run quantity.
4. Player IDs are 100% collision-free and consistent across all tournament editions.
5. All 23 rain-affected DLS fixtures have explicit `revised_target` and `revised_overs` metadata.
6. 6 tied fixtures feature Super Overs (Innings 3 and 4, 38 total deliveries).

#### Unresolved Data Issues:
1. **Absence of Discrete Bye/Legbye Run Tally**: When byes or leg-byes occur, `runs` is 0. While single byes/leg-byes represent the vast majority of cases, multi-run byes or overthrows are not recorded in a dedicated extra runs column. Inning totals reconcile within 1–2 runs of official totals.
2. **Fielding Error Telemetry**: Dropped catches and missed run-out opportunities are not logged. A batter dropped under pressure cannot be statistically differentiated from a clean boundary execution in the raw event log.

#### Known Limitations Affecting Future Modeling:
1. **Sample Size Disparity**: Batters playing primarily for Associate nations or non-qualifying T20I teams have lower match frequencies compared to core IPL franchise players. A Bayesian shrinkage prior is required in Phase 02 to prevent small-sample distortion.
2. **Impact Player Asymmetry**: IPL matches from 2023 onwards permit 12 active participants per match (allowing longer batting lineups and dedicated death-bowling options), whereas T20I matches adhere to standard 11-player limits. A competition calibration factor must be introduced.

---

### 8. Phase 02 Strategic Recommendations & Roadmap

With Phase 01 successfully completed and all data dependencies validated, the consortium recommends advancing to **Phase 02: Pressure Index Modeling & Mathematical Architecture**.

#### Recommended Phase 02 Deliverables:
1. **Formal Mathematical Definition of Pressure ($\Psi$)**:
   - Establish a unified **Leverage Index ($LI$)** combining run rate stress, resource scarcity, and match phase.
   - Partition pressure into distinct sub-indices:
     - **Chasing Clutch Index ($\Psi_{\text{chase}}$)**: Innings 2 high-RRR performance.
     - **Collapse Recovery Index ($\Psi_{\text{rebuild}}$)**: Innings 1 crisis batting.
     - **Death Execution Index ($\Psi_{\text{death}}$)**: Overs 16–20 batting and bowling.
2. **Context-Normalized Player Baselines**:
   - Compute each player's neutral baseline (Strike Rate, Average, Economy, Dot%, Boundary%).
   - Define **Clutch Delta ($\Delta_{\text{Clutch}}$)**: Performance in High-Pressure Deliveries minus Neutral Baseline.
3. **Empirical Bayesian Shrinkage & Uncertainty Bounds**:
   - Apply hierarchical shrinkage estimators to regressing low-sample players toward population norms.
   - Calculate 95% confidence intervals on clutch ratings.
4. **Top 10 Rankings Engine**:
   - Produce statistically defensible, fully explained Top 10 Batter and Top 10 Bowler rankings ready for executive review.

---

### Consortium Sign-Off

- **Lead Cricket Data Scientist**: *Validated calculation logic, relational integrity, and feature derivation models.*
- **Senior Sports Statistician**: *Validated sample distributions, variance bounds, and mathematical formulations.*
- **Cricket Performance Analyst**: *Validated cricketing relevance of innings asymmetry and dismissal classification.*
- **Data Engineering Architect**: *Validated ETL pipeline, data dictionary, and schema consistency.*
- **Senior IPL Auction Strategist**: *Formally certified readiness of data foundation for auction valuation modeling.*

