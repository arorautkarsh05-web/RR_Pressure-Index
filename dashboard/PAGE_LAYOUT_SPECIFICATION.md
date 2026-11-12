# RR AUCTION INTELLIGENCE 2027: PAGE LAYOUT & VISUAL WIREFRAME SPECIFICATION
## Comprehensive 6-Page UI/UX Design System for Power BI

**Product Name**: RR AUCTION INTELLIGENCE 2027  
**Subtitle**: Pressure Performance & Player Reliability Command Center  
**Resolution**: Standard 16:9 Canvas (1920 x 1080 pixels)  
**Theme**: Deep Midnight Navy (`#0B132B`) with Rajasthan Royal Pink (`#E81B84`) and Electric Blue (`#004BA0`) Accents  
**Typography**: Segoe UI Semibold (Headers / KPIs), Segoe UI (Body / Data Values)

---

## PAGE 01 — EXECUTIVE COMMAND CENTER

### Purpose
The high-level executive dashboard presenting validated macro metrics, Top 5 Batters and Bowlers, performance distributions, and traceable franchise auction insights.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ HEADER: RR AUCTION INTELLIGENCE 2027 — Pressure Performance & Player Reliability Command Center │
├───────────────┬───────────────┬───────────────┬───────────────┬────────────────┬─────────────────┤
│ SENIOR MATCHES│ TOTAL BALLS   │ PLAYERS MODEL │ QUAL. BATTERS │ QUAL. BOWLERS  │ PRESSURE BALLS  │
│ 837           │ 194,014       │ 891           │ 92 (Tier A/B) │ 167 (Tier A/B) │ 24,016 / 41,202 │
├───────────────┴───────────────┴───────────────┴───────────────┴────────────────┴─────────────────┤
│ [VISUAL 1: TOP 5 BATTERS CPRI]                │ [VISUAL 2: TOP 5 BOWLERS CPRI]                   │
│ Horizontal Bar Chart with 95% Error Bars      │ Horizontal Bar Chart with 95% Error Bars         │
│ Dhir (74.4) | David (72.5) | Salt (71.8) ...  │ Bumrah (76.8) | Raza (75.6) | Rauf (74.1) ...    │
├───────────────────────────────────────────────┼──────────────────────────────────────────────────┤
│ [VISUAL 3: BATTING PRESSURE VS NORMAL SR]     │ [VISUAL 4: BOWLING LEVERAGE VS NORMAL ECON]      │
│ Scatter Quadrant: Baseline SR vs Pressure SR  │ Scatter Quadrant: Baseline Econ vs Leverage Econ │
│ Color: Delta Context SR                       │ Color: Delta Context Econ                        │
├───────────────────────────────────────────────┴──────────────────────────────────────────────────┤
│ [EXECUTIVE DATA-DERIVED INSIGHTS PANEL]                                                          │
│ • Elite Multi-Arena Anchors: Bumrah (576 IPL balls, 6.95 econ) & David (199.2 IPL SR) anchor.  │
│ • Domestic Finishing Value: Ashutosh Sharma (140 IPL balls, 193.4 SR, 3.26% outlier drop).       │
│ • High-Variance Foreign Risk: Haris Rauf & George Dockrell have 0 IPL balls; require discounting.│
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Visual Component Specifications

1. **Header Banner & Slicers**
   - Coordinates: $X=20, Y=20, W=1880, H=80$
   - Tournament Slicer: "All Competitions", "IPL Only", "T20I Only" (Segmented button).
   - Evidence Tier Slicer: "Tier 1 Marquee Core", "Tier 2 High-Upside", "Tier 3 Tactical", "Tier 4 Foreign".

2. **KPI Card Grid (6 Cards)**
   - Dimensions: $W=300, H=100$ each.
   - Card 1: `[Senior Matches Analysed]` — Value: `837` | Subtitle: "470 T20I / 367 IPL"
   - Card 2: `[Total Senior Deliveries]` — Value: `194,014` | Subtitle: "186,540 Bat / 185,715 Bowl"
   - Card 3: `[Unique Players Evaluated]` — Value: `891` | Subtitle: "1,235 Baseline Profiles"
   - Card 4: `[Qualified Batters]` — Value: `92` | Subtitle: "$\ge 50$ Pressure Deliveries"
   - Card 5: `[Qualified Bowlers]` — Value: `167` | Subtitle: "$\ge 60$ Leverage Deliveries"
   - Card 6: `[Pressure Deliveries]` — Value: `65,218` | Subtitle: "24,016 Bat / 41,202 Bowl"

3. **Visual 1 & 2: Top 5 Reliability Leaderboards**
   - Coordinates: Visual 1 ($X=20, Y=220, W=920, H=340$), Visual 2 ($X=960, Y=220, W=940, H=340$)
   - Type: Clustered Horizontal Bar Chart.
   - Y-Axis: `DimRanking[PlayerName]` (Filtered to Rank 1–5).
   - X-Axis: `[Official CPRI Score]` (Range: 60 to 80).
   - Error Bars: Lower Bound = `[CPRI CI Low]`, Upper Bound = `[CPRI CI High]`.
   - Data Labels: Show value (`0.00`) and rank badge.

4. **Visual 3 & 4: Performance vs Baseline Quadrants**
   - Coordinates: Visual 3 ($X=20, Y=580, W=920, H=320$), Visual 4 ($X=960, Y=580, W=940, H=320$)
   - Visual 3 (Batting): X-Axis = `[Normal Baseline Strike Rate]`, Y-Axis = `[Pressure Strike Rate]`, Size = `[Pressure Deliveries Faced]`, Color = `[Delta Context Strike Rate]`.
   - Visual 4 (Bowling): X-Axis = `[Normal Baseline Economy Rate]`, Y-Axis = `[Leverage Economy Rate]`, Size = `[Leverage Deliveries Bowled]`, Color = `[Delta Context Economy Rate]`.
   - Reference Lines: Population Averages (Batting Par = 133.6 SR; Bowling Par = 8.15 Econ).

5. **Executive Insights Card**
   - Coordinates: $X=20, Y=920, W=1880, H=140$
   - Background: Dark Glass Card (`#151E3F`, border `#243356`).
   - Content: Traceable analytical findings linked to player metrics.

---

## PAGE 02 — BATTING INTELLIGENCE

### Purpose
Exhaustive evaluation of batting clutch capability, comparing pressure execution against normal baselines, boundary acceleration, dot-ball suppression, and Bayesian uncertainty.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ HEADER: BATTING PERFORMANCE & PRESSURE RELIABILITY                                               │
├─────────────────────────────────────────────────┬────────────────────────────────────────────────┤
│ [OFFICIAL TOP 10 BATTERS RANKING TABLE]         │ [SELECTED PLAYER DETAIL DOSSIER]               │
│ Rank | Player | Press SR | Delta SR | Bayes SR  │ • Player Profile & Age / Primary Role          │
│ 1    | Naman  | 215.38   | +69.14   | 195.15    │ • Total Senior Matches & Balls Faced           │
│ 2    | David  | 203.86   | +59.17   | 195.00    │ • Normal SR vs. Pressure SR (+Delta)           │
│ 3    | Salt   | 232.73   | +87.86   | 199.00    │ • Boundary % (29.1%) vs Dot % (23.1%)          │
│ 4    | Buttler| 189.04   | +51.08   | 180.34    │ • Match Consistency CV (0.187) & Success (100%)│
│ ...  | ...    | ...      | ...      | ...       │ • Posterior CI Interval & Worst-Case LOMO Rank │
├─────────────────────────────────────────────────┼────────────────────────────────────────────────┤
│ [SCATTER: BOUNDARY % VS DOT-BALL SUPPRESSION]   │ [POSTERIOR UNCERTAINTY ERROR BAR CHART]        │
│ X-Axis: Dot % | Y-Axis: Boundary %              │ Point Estimate: Bayes SR | Error Bar: 95% CI   │
│ Size: Pressure Balls | Color: CPRI              │ Narrowest CI: Suryakumar (42.4) vs Dhir (72.4) │
├─────────────────────────────────────────────────┴────────────────────────────────────────────────┤
│ [SITUATIONAL SPLIT BAR CHART]                                                                    │
│ Chasing Clutch SR vs Collapse Recovery SR vs Death Overs Finishing SR                            │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Table Columns
1. **Rank**: `DimRanking[OfficialRank]`
2. **Player**: `DimRanking[PlayerName]`
3. **Pressure Strike Rate**: `[Pressure Strike Rate]` (`0.00`)
4. **Context-Adjusted Delta**: `[Delta Context Strike Rate]` (`+0.00`)
5. **Pressure Balls**: `[Pressure Deliveries Faced]` (`#,##0`)
6. **Qualified Matches**: `[Qualified Pressure Matches]`
7. **Bayes Estimate SR**: `[Bayes Estimate Rate]` (`0.00`)
8. **95% Credible Interval**: `[Bayes CI Low]` – `[Bayes CI High]`
9. **Match Consistency CV**: `[Match Level CV]` (`0.000`)
10. **Evidence Tier**: `DimRanking[OverallEvidenceTier]`

---

## PAGE 03 — BOWLING INTELLIGENCE

### Purpose
Exhaustive evaluation of bowling execution leverage, measuring run suppression, boundary concession denial, dot-ball creation, and wicket strike rate under crisis situations.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ HEADER: BOWLING EXECUTION & PRESSURE RELIABILITY                                                 │
├─────────────────────────────────────────────────┬────────────────────────────────────────────────┤
│ [OFFICIAL TOP 10 BOWLERS RANKING TABLE]         │ [SELECTED BOWLER DETAIL DOSSIER]               │
│ Rank | Player  | Lev Econ | Delta Econ | Bayes  │ • Player Profile & Primary Role                │
│ 1    | Bumrah  | 6.94     | -1.97      | 7.01   │ • Total Senior Deliveries Bowled               │
│ 2    | Raza    | 6.44     | -1.84      | 6.98   │ • Normal Economy vs Leverage Economy           │
│ 3    | Rauf    | 7.56     | -1.28      | 7.78   │ • Boundary Concession % (14.2%) vs Dot % (40%) │
│ 4    | Dockrell| 5.29     | -2.96      | 7.23   │ • Wicket Taking Strike Rate (19.2 balls/wkt)   │
│ 5    | Imad    | 5.77     | -2.47      | 7.08   │ • Match Consistency CV (0.473) & Success (72%) │
│ ...  | ...     | ...      | ...        | ...    │ • Posterior CI Interval & Jackknife SE (0.44)  │
├─────────────────────────────────────────────────┼────────────────────────────────────────────────┤
│ [SCATTER: WICKET STRIKE RATE VS BOUNDARY DENIAL]│ [POSTERIOR UNCERTAINTY ERROR BAR CHART]        │
│ X-Axis: Conceded Boundary % | Y-Axis: Wkt SR    │ Point Estimate: Bayes Econ | Error Bar: 95% CI │
│ Bubble Size: Leverage Balls Bowled              │ Narrowest CI: Bumrah (1.69) vs Dockrell (3.85) │
├─────────────────────────────────────────────────┴────────────────────────────────────────────────┤
│ [PHASE EXECUTION MATRIX]                                                                         │
│ Powerplay Leverage Economy vs Middle-Overs Containment vs Death Yorker Execution                 │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## PAGE 04 — PLAYER COMPARISON LAB

### Purpose
Side-by-side bivariate benchmarking between two or three shortlisted players within the same discipline to resolve auction trade-offs.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ HEADER: PLAYER COMPARISON LAB — Head-to-Head Reliability Benchmarking                            │
├────────────────────────────────┬────────────────────────────────┬────────────────────────────────┤
│ [SELECTOR A: PLAYER 1]         │ [SELECTOR B: PLAYER 2]         │ [SELECTOR C: PLAYER 3 (OPT)]   │
│ Dropdown: Naman Dhir           │ Dropdown: Tim David            │ Dropdown: Ashutosh Sharma      │
├────────────────────────────────┴────────────────────────────────┴────────────────────────────────┤
│ [RADAR / METRIC COMPARISON MATRIX]                                                               │
│ Metric                   │ Player 1 (Dhir)        │ Player 2 (David)       │ Delta (P1 vs P2)    │
│ Pressure Strike Rate     │ 215.38                 │ 203.86                 │ +11.52 SR (Dhir)    │
│ Context Delta SR         │ +69.14                 │ +59.17                 │ +9.97 Delta (Dhir)  │
│ Pressure Balls Faced     │ 91                     │ 207                    │ -116 balls (David)  │
│ 95% CI Width             │ 72.37 (Tier B)         │ 52.57 (Tier A)         │ -19.80 (David More) │
│ Match Consistency CV     │ 0.187 (Elite)          │ 0.425 (Solid)          │ -0.238 (Dhir More)  │
│ Outlier Drop %           │ -5.41% (Robust)        │ -3.55% (Robust)        │ Both Highly Robust  │
│ IPL Sample Exposure      │ 62 balls               │ 124 balls              │ David 2x IPL Volume │
│ Evidence Tier            │ Tier 2 High-Upside     │ Tier 1 Marquee Core    │ David Marquee       │
├────────────────────────────────────────────────┬─────────────────────────────────────────────────┤
│ [SITUATIONAL HEAD-TO-HEAD BARS]                │ [MATCH-BY-MATCH TRAJECTORY LINE CHART]          │
│ Chase vs Death Phase Comparison                │ Game-by-game scoring rate across tournaments     │
└────────────────────────────────────────────────┴─────────────────────────────────────────────────┘
```

---

## PAGE 05 — AUCTION INTELLIGENCE & TRANSFERABILITY

### Purpose
Franchise decision-support module applying the 5-Dimension Evidence Framework to evaluate auction capital allocation, competition transferability, and tactical squad fitment.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ HEADER: PLAYER SCOUTING & AUCTION TRANSFERABILITY                                                │
├─────────────────────────────────────────────────┬────────────────────────────────────────────────┤
│ [5-DIMENSION EVIDENCE SQUAD MATRIX]             │ [EVIDENCE TIER DISTRIBUTION]                   │
│ Player | Role | IPL Balls | T20I Balls | Tier   │ Donut Chart: Tier 1 (35%), Tier 2 (15%),       │
│ Bumrah | Bowl | 576       | 187        | Tier 1 │ Tier 3 (10%), Tier 4 (40%)                     │
│ David  | Bat  | 124       | 83         | Tier 1 ├────────────────────────────────────────────────┤
│ Dhir   | Bat  | 62        | 29         | Tier 2 │ [IPL VS T20I SCATTER QUADRANT]                 │
│ Rauf   | Bowl | 0         | 505        | Tier 4 │ X: T20I Volume | Y: IPL Volume                 │
│ Salt   | Bat  | 4         | 51         | Tier 3 │ Quadrant IV: T20I Exclusive (High Risk)        │
├─────────────────────────────────────────────────┴────────────────────────────────────────────────┤
│ [TACTICAL SQUAD FITMENT & PURSE MULTIPLIER CALCULATOR]                                           │
│ Target Role: Death Finisher | Powerplay Enforcer | Crisis Anchor | Yorker Specialist             │
│ Hypothetical Purse Multiplier: Tier 1 = 2.5x-3.0x | Tier 2 = 1.8x-2.2x | Tier 4 = Scenario Disct │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## PAGE 06 — STATISTICAL METHODOLOGY

### Purpose
Full mathematical transparency and documentation of Bayesian reliability modeling, pressure indices ($\Psi_{\text{bat}}, \lambda_{\text{bowl}}$), credible interval derivation, and limitations.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ HEADER: STATISTICAL METHODOLOGY & RELIABILITY ARCHITECTURE                                       │
├────────────────────────────────┬────────────────────────────────┬────────────────────────────────┤
│ [1. PRESSURE FORMULATION]      │ [2. BAYESIAN RELIABILITY]      │ [3. CERTIFIED RECONCILIATION]  │
│ Equations for Psi & Lambda     │ Empirical Bayes Shrinkage:     │ • 194,014 Evaluated Balls      │
│ Required Run Rate Deficit      │ theta_shrunk = W*theta + (1-W)mu│ • 186,540 Bat / 185,715 Bowl   │
│ Wickets in Hand Constraints    │ Prior Weight M0 = 25 balls     │ • 825 No-Balls Reconciled      │
│ Pure Pre-Delivery Metrics      │ Credible Intervals: Ka = 1.96  │ • 64 Bumrah Leverage Matches   │
├────────────────────────────────┴────────────────────────────────┴────────────────────────────────┤
│ [BAYESIAN SHRINKAGE VISUALIZATION: RAW VS SHRUNK ESTIMATES]                                      │
│ Scatter Plot: Raw Pressure Metric vs Bayes Posterior Mean                                        │
│ Low Sample Points pulled toward Population Mean (133.6 SR / 8.15 Econ)                            │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [DATA LIMITATIONS & ASSUMPTIONS ACCORDION]                                                       │
│ • Venue pitch telemetry (black vs red clay) absent from raw dataset; accounted via context par. │
│ • All-rounders evaluated separately per discipline (379 profiles reconciled).                   │
│ • Zero outcome leakage guaranteed (all pressure variables strictly pre-delivery).               │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

