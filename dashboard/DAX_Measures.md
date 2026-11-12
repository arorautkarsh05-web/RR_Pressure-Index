# RR AUCTION INTELLIGENCE 2027: DAX MEASURES SPECIFICATION
## Certified Measure Reference for Microsoft Power BI Desktop

**Data Model**: Star Schema (Import Mode)  
**Tables Referenced**: `FactDeliveryPressure`, `FactPlayerMatchPerformance`, `FactPlayerPressurePerformance`, `DimPlayer`, `DimMatch`, `DimCompetition`, `DimRanking`, `DimContext`

---

### Folder: `1. Volume & Filter Measures`

#### 1.1 `[Total Deliveries Faced]`
- **Description**: Total legal deliveries faced by batters (excludes wides; includes no-balls).
- **Format**: `#,##0`
- **DAX**:
```dax
[Total Deliveries Faced] = 
CALCULATE(
    COUNTROWS(FactDeliveryPressure),
    FactDeliveryPressure[IsLegalBatting] = 1
)
```

#### 1.2 `[Total Deliveries Bowled]`
- **Description**: Total legal deliveries bowled by bowlers (excludes wides and no-balls). Uses inactive relationship on `BowlerID`.
- **Format**: `#,##0`
- **DAX**:
```dax
[Total Deliveries Bowled] = 
CALCULATE(
    COUNTROWS(FactDeliveryPressure),
    FactDeliveryPressure[IsLegalBowling] = 1,
    USERELATIONSHIP(DimPlayer[PlayerID], FactDeliveryPressure[BowlerID])
)
```

#### 1.3 `[Pressure Deliveries Faced]`
- **Description**: Total legal deliveries faced by batters under certified high-pressure match states ($\Psi_{\text{bat}} = 1$).
- **Format**: `#,##0`
- **DAX**:
```dax
[Pressure Deliveries Faced] = 
CALCULATE(
    [Total Deliveries Faced],
    FactDeliveryPressure[IsBatPressure] = 1
)
```

#### 1.4 `[Leverage Deliveries Bowled]`
- **Description**: Total legal deliveries bowled under certified high bowling leverage match states ($\lambda_{\text{bowl}} = 1$).
- **Format**: `#,##0`
- **DAX**:
```dax
[Leverage Deliveries Bowled] = 
CALCULATE(
    [Total Deliveries Bowled],
    FactDeliveryPressure[IsBowlLeverage] = 1
)
```

#### 1.5 `[Pressure Exposure Share Bat %]`
- **Description**: Percentage of a batter's total balls faced that occurred under high pressure.
- **Format**: `0.0%`
- **DAX**:
```dax
[Pressure Exposure Share Bat %] = 
DIVIDE([Pressure Deliveries Faced], [Total Deliveries Faced], BLANK())
```

#### 1.6 `[Leverage Exposure Share Bowl %]`
- **Description**: Percentage of a bowler's total legal deliveries that were bowled under high leverage.
- **Format**: `0.0%`
- **DAX**:
```dax
[Leverage Exposure Share Bowl %] = 
DIVIDE([Leverage Deliveries Bowled], [Total Deliveries Bowled], BLANK())
```

---

### Folder: `2. Performance Rates`

#### 2.1 `[Pressure Strike Rate]`
- **Description**: Batting strike rate under pressure (runs off the bat divided by pressure balls faced $\times 100$).
- **Format**: `0.00`
- **DAX**:
```dax
[Pressure Strike Rate] = 
DIVIDE(
    CALCULATE(
        SUM(FactDeliveryPressure[RunsBat]),
        FactDeliveryPressure[IsBatPressure] = 1,
        FactDeliveryPressure[IsLegalBatting] = 1
    ) * 100.0,
    [Pressure Deliveries Faced],
    BLANK()
)
```

#### 2.2 `[Normal Baseline Strike Rate]`
- **Description**: Batting strike rate under normal match baseline conditions ($\Psi_{\text{bat}} = 0$).
- **Format**: `0.00`
- **DAX**:
```dax
[Normal Baseline Strike Rate] = 
DIVIDE(
    CALCULATE(
        SUM(FactDeliveryPressure[RunsBat]),
        FactDeliveryPressure[IsBatPressure] = 0,
        FactDeliveryPressure[IsLegalBatting] = 1
    ) * 100.0,
    CALCULATE([Total Deliveries Faced], FactDeliveryPressure[IsBatPressure] = 0),
    BLANK()
)
```

#### 2.3 `[Delta Context Strike Rate]`
- **Description**: Pressure Strike Rate minus Normal Baseline Strike Rate. Positive values indicate situational elevation.
- **Format**: `+0.00;-0.00;0.00`
- **DAX**:
```dax
[Delta Context Strike Rate] = 
[Pressure Strike Rate] - [Normal Baseline Strike Rate]
```

#### 2.4 `[Leverage Economy Rate]`
- **Description**: Bowling economy under high leverage (bowler runs conceded divided by leverage legal balls $\times 6.0$).
- **Format**: `0.00`
- **DAX**:
```dax
[Leverage Economy Rate] = 
DIVIDE(
    CALCULATE(
        SUM(FactDeliveryPressure[BowlerRunsConceded]),
        FactDeliveryPressure[IsBowlLeverage] = 1,
        USERELATIONSHIP(DimPlayer[PlayerID], FactDeliveryPressure[BowlerID])
    ) * 6.0,
    [Leverage Deliveries Bowled],
    BLANK()
)
```

#### 2.5 `[Normal Baseline Economy Rate]`
- **Description**: Bowling economy under normal match baseline conditions ($\lambda_{\text{bowl}} = 0$).
- **Format**: `0.00`
- **DAX**:
```dax
[Normal Baseline Economy Rate] = 
DIVIDE(
    CALCULATE(
        SUM(FactDeliveryPressure[BowlerRunsConceded]),
        FactDeliveryPressure[IsBowlLeverage] = 0,
        USERELATIONSHIP(DimPlayer[PlayerID], FactDeliveryPressure[BowlerID])
    ) * 6.0,
    CALCULATE([Total Deliveries Bowled], FactDeliveryPressure[IsBowlLeverage] = 0),
    BLANK()
)
```

#### 2.6 `[Delta Context Economy Rate]`
- **Description**: Leverage Economy Rate minus Normal Baseline Economy Rate. Negative values indicate run suppression under pressure.
- **Format**: `-0.00;+0.00;0.00`
- **DAX**:
```dax
[Delta Context Economy Rate] = 
[Leverage Economy Rate] - [Normal Baseline Economy Rate]
```

---

### Folder: `3. Boundary & Dot-Ball Execution`

#### 3.1 `[Pressure Boundary %]`
- **Description**: Proportion of pressure deliveries hit for 4 or 6.
- **Format**: `0.0%`
- **DAX**:
```dax
[Pressure Boundary %] = 
DIVIDE(
    CALCULATE(
        SUM(FactDeliveryPressure[IsFour]) + SUM(FactDeliveryPressure[IsSix]),
        FactDeliveryPressure[IsBatPressure] = 1,
        FactDeliveryPressure[IsLegalBatting] = 1
    ),
    [Pressure Deliveries Faced],
    BLANK()
)
```

#### 3.2 `[Pressure Dot %]`
- **Description**: Proportion of pressure deliveries resulting in zero runs off the bat.
- **Format**: `0.0%`
- **DAX**:
```dax
[Pressure Dot %] = 
DIVIDE(
    CALCULATE(
        COUNTROWS(FactDeliveryPressure),
        FactDeliveryPressure[IsBatPressure] = 1,
        FactDeliveryPressure[RunsBat] = 0,
        FactDeliveryPressure[IsLegalBatting] = 1
    ),
    [Pressure Deliveries Faced],
    BLANK()
)
```

#### 3.3 `[Leverage Conceded Boundary %]`
- **Description**: Proportion of leverage legal deliveries hit for boundary (4 or 6).
- **Format**: `0.0%`
- **DAX**:
```dax
[Leverage Conceded Boundary %] = 
DIVIDE(
    CALCULATE(
        SUM(FactDeliveryPressure[IsFour]) + SUM(FactDeliveryPressure[IsSix]),
        FactDeliveryPressure[IsBowlLeverage] = 1,
        FactDeliveryPressure[IsLegalBowling] = 1,
        USERELATIONSHIP(DimPlayer[PlayerID], FactDeliveryPressure[BowlerID])
    ),
    [Leverage Deliveries Bowled],
    BLANK()
)
```

#### 3.4 `[Leverage Dot %]`
- **Description**: Proportion of leverage legal deliveries resulting in zero runs conceded.
- **Format**: `0.0%`
- **DAX**:
```dax
[Leverage Dot %] = 
DIVIDE(
    CALCULATE(
        COUNTROWS(FactDeliveryPressure),
        FactDeliveryPressure[IsBowlLeverage] = 1,
        FactDeliveryPressure[BowlerRunsConceded] = 0,
        FactDeliveryPressure[IsLegalBowling] = 1,
        USERELATIONSHIP(DimPlayer[PlayerID], FactDeliveryPressure[BowlerID])
    ),
    [Leverage Deliveries Bowled],
    BLANK()
)
```

#### 3.5 `[Leverage Wicket Strike Rate]`
- **Description**: Balls bowled per wicket taken under leverage (lower is more lethal).
- **Format**: `0.0`
- **DAX**:
```dax
[Leverage Wicket Strike Rate] = 
DIVIDE(
    [Leverage Deliveries Bowled],
    CALCULATE(
        SUM(FactDeliveryPressure[IsBowlerWicket]),
        FactDeliveryPressure[IsBowlLeverage] = 1,
        USERELATIONSHIP(DimPlayer[PlayerID], FactDeliveryPressure[BowlerID])
    ),
    BLANK()
)
```

---

### Folder: `4. Bayesian & Credible Intervals`

#### 4.1 `[Bayes Estimate Rate]`
- **Description**: Shrunk posterior mean estimate for SR (batters) or Economy (bowlers). Directly imported from certified empirical Bayes pipeline.
- **Format**: `0.00`
- **DAX**:
```dax
[Bayes Estimate Rate] = 
SELECTEDVALUE(FactPlayerPressurePerformance[BayesEstimate])
```

#### 4.2 `[Bayes CI Low]`
- **Description**: 2.5th percentile of posterior credible distribution.
- **Format**: `0.00`
- **DAX**:
```dax
[Bayes CI Low] = 
SELECTEDVALUE(FactPlayerPressurePerformance[Bayes_CI_Low])
```

#### 4.3 `[Bayes CI High]`
- **Description**: 97.5th percentile of posterior credible distribution.
- **Format**: `0.00`
- **DAX**:
```dax
[Bayes CI High] = 
SELECTEDVALUE(FactPlayerPressurePerformance[Bayes_CI_High])
```

#### 4.4 `[Bayes Error Margin]`
- **Description**: Half-width of the 95% posterior credible interval ($\pm \text{Margin}$).
- **Format**: `0.00`
- **DAX**:
```dax
[Bayes Error Margin] = 
DIVIDE(
    [Bayes CI High] - [Bayes CI Low],
    2.0,
    BLANK()
)
```

---

### Folder: `5. CPRI & Official Rankings`

#### 5.1 `[Official CPRI Score]`
- **Description**: Composite Pressure Reliability Index (0–100 scale).
- **Format**: `0.00`
- **DAX**:
```dax
[Official CPRI Score] = 
SELECTEDVALUE(DimRanking[CPRI])
```

#### 5.2 `[CPRI CI Low]`
- **Description**: Lower bound of 95% credible interval for CPRI.
- **Format**: `0.00`
- **DAX**:
```dax
[CPRI CI Low] = 
SELECTEDVALUE(DimRanking[CPRI_CI_Low])
```

#### 5.3 `[CPRI CI High]`
- **Description**: Upper bound of 95% credible interval for CPRI.
- **Format**: `0.00`
- **DAX**:
```dax
[CPRI CI High] = 
SELECTEDVALUE(DimRanking[CPRI_CI_High])
```

#### 5.4 `[Official Rank Number]`
- **Description**: Official certified rank (1–10).
- **Format**: `0`
- **DAX**:
```dax
[Official Rank Number] = 
SELECTEDVALUE(DimRanking[OfficialRank])
```

---

### Folder: `6. Consistency & Jackknife Robustness`

#### 6.1 `[Match Level CV]`
- **Description**: Individual match-to-match coefficient of variation ($\sigma_{\text{match}} / \mu_{\text{match}}$). Lower indicates night-to-night consistency.
- **Format**: `0.000`
- **DAX**:
```dax
[Match Level CV] = 
SELECTEDVALUE(FactPlayerPressurePerformance[MatchCV])
```

#### 6.2 `[Match Success Rate %]`
- **Description**: Percentage of qualified pressure matches meeting performance target ($\ge 140$ SR or $\le 8.5$ Econ).
- **Format**: `0.0%`
- **DAX**:
```dax
[Match Success Rate %] = 
SELECTEDVALUE(FactPlayerPressurePerformance[MatchSuccessRate])
```

#### 6.3 `[Jackknife Worst Case Metric]`
- **Description**: Performance metric under the worst-case scenario where the player's single most impactful match is dropped.
- **Format**: `0.00`
- **DAX**:
```dax
[Jackknife Worst Case Metric] = 
SELECTEDVALUE(FactPlayerPressurePerformance[JackknifeWorstCaseMetric])
```

#### 6.4 `[Jackknife Standard Error]`
- **Description**: Leave-One-Match-Out Jackknife standard error.
- **Format**: `0.00`
- **DAX**:
```dax
[Jackknife Standard Error] = 
SELECTEDVALUE(FactPlayerPressurePerformance[JackknifeSE])
```

---

### Folder: `7. Auction Intelligence & Evidence Tiering`

#### 7.1 `[Overall Auction Evidence Tier]`
- **Description**: Certified 5-Dimension Evidence Tier (Tier 1 Marquee Core / Tier 2 High-Upside / Tier 3 Tactical / Tier 4 Foreign Target).
- **Format**: Text
- **DAX**:
```dax
[Overall Auction Evidence Tier] = 
SELECTEDVALUE(DimRanking[OverallEvidenceTier])
```

#### 7.2 `[Auction Purse Multiplier]`
- **Description**: Recommended purse allocation multiplier range based on certified rank tier.
- **Format**: Text
- **DAX**:
```dax
[Auction Purse Multiplier] = 
SWITCH(
    [Official Rank Number],
    1, "2.5x - 3.0x Baseline",
    2, "2.5x - 3.0x Baseline",
    3, "2.5x - 3.0x Baseline",
    4, "2.2x - 2.5x Baseline",
    5, "1.8x - 2.2x Baseline",
    6, "1.8x - 2.2x Baseline",
    7, "1.8x - 2.2x Baseline",
    8, "1.5x - 1.8x Baseline",
    9, "1.5x - 1.8x Baseline",
    10, "1.2x - 1.5x Baseline",
    "1.0x Baseline"
)
```

#### 7.3 `[Selected Player Title Header]`
- **Description**: Dynamic header string for visual cards and detail panels.
- **Format**: Text
- **DAX**:
```dax
[Selected Player Title Header] = 
VAR PName = SELECTEDVALUE(DimPlayer[PlayerName], "All Players (Cohort Summary)")
VAR RNum = SELECTEDVALUE(DimRanking[OfficialRank], 0)
VAR Disc = SELECTEDVALUE(DimRanking[Discipline], "")
VAR CPRI_Val = [Official CPRI Score]
RETURN
IF(
    RNum > 0,
    PName & " — Rank #" & RNum & " " & Disc & " (CPRI: " & FORMAT(CPRI_Val, "0.00") & ")",
    PName
)
```

#### 7.4 `[Linguistic Governance Status]`
- **Description**: Enforces certified non-misleading terminology for executives and judges.
- **Format**: Text
- **DAX**:
```dax
[Linguistic Governance Status] = 
SWITCH(
    [Official Rank Number],
    1, "Certified Top 10 Contender (Leading Tier)",
    2, "Certified Top 10 Contender (Elite Core)",
    3, "Certified Top 10 Asset",
    4, "Certified Top 10 Asset",
    5, "Certified Top 10 Asset",
    "Certified Tactical Asset"
)
```

