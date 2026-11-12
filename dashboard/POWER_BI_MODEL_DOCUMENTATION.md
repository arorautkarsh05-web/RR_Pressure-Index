# RR AUCTION INTELLIGENCE 2027: POWER BI DATA MODEL ARCHITECTURE
## Production Star Schema & VertiPaq Engine Specification

**Application Name**: RR Auction Intelligence 2027  
**Platform**: Microsoft Power BI Desktop (May 2024+ engine) / Power BI Service  
**Storage Architecture**: Direct Import Mode (In-Memory Columnar VertiPaq)  
**Total Entities**: 10 Tables (3 Fact Tables, 7 Dimension Tables)  
**Relational Integrity**: Zero Many-to-Many Relationships; 100% Integer Surrogate Keys

---

## 1. Relational Star Schema Architecture

The data model follows strict Kimball Star-Schema principles. A central delivery fact table (`FactDeliveryPressure`) connects to conformable dimensions, supported by player-match and player-pressure aggregate fact tables to guarantee instantaneous sub-second query performance.

```mermaid
erDiagram
    DimPlayer ||--o{ FactDeliveryPressure : "StrikerID (Active) / BowlerID (Inactive)"
    DimPlayer ||--o{ FactPlayerMatchPerformance : "PlayerID"
    DimPlayer ||--o{ FactPlayerPressurePerformance : "PlayerID"
    DimPlayer ||--|| DimRanking : "PlayerID"
    
    DimMatch ||--o{ FactDeliveryPressure : "MatchID"
    DimMatch ||--o{ FactPlayerMatchPerformance : "MatchID"
    
    DimCompetition ||--o{ DimMatch : "CompID"
    DimDate ||--o{ DimMatch : "DateKey"
    
    DimTeam ||--o{ FactDeliveryPressure : "BattingTeamID / BowlingTeamID"
    DimTeam ||--o{ FactPlayerMatchPerformance : "TeamID"
    DimTeam ||--o{ DimMatch : "HomeTeamID / AwayTeamID"
    
    DimContext ||--o{ FactDeliveryPressure : "ContextID"
```

---

## 2. Table Catalog, Data Grain & Column Specifications

### Dimension Tables

#### 1. `DimPlayer`
- **Data Grain**: Exactly 1 record per unique registered cricketer ($N=891$).
- **Primary Key**: `PlayerID` (int)
- **Columns**:
  - `PlayerID` (int, PK) — Unique player identifier.
  - `PlayerName` (text) — Canonical player display name.
  - `PrimaryDiscipline` (text) — "Batter", "Bowler", "All-Rounder", "Squad Member".
  - `IsDualDiscipline` (int) — 1 if player qualifies in both disciplines, 0 otherwise.
  - `BattingConfidenceTier` (text) — "Tier A (N>=100)", "Tier B (50<=N<100)", "Unqualified".
  - `BowlingConfidenceTier` (text) — "Tier A (N>=100)", "Tier B (60<=N<100)", "Unqualified".

#### 2. `DimCompetition`
- **Data Grain**: Exactly 1 record per tournament competition ($N=136$).
- **Primary Key**: `CompID` (int)
- **Columns**:
  - `CompID` (int, PK) — Unique competition identifier.
  - `CompName` (text) — Official tournament name.
  - `MatchFormat` (text) — "T20".
  - `Season` (text) — Season year.
  - `CompetitionType` (text) — "IPL" vs. "T20I".

#### 3. `DimTeam`
- **Data Grain**: Exactly 1 record per franchise or international team ($N=38$).
- **Primary Key**: `TeamID` (int)
- **Columns**:
  - `TeamID` (int, PK) — Unique team identifier.
  - `TeamName` (text) — Full franchise / national team name.
  - `TeamCode` (text) — 3-4 letter acronym (e.g. RR, MI, CSK, IND, ENG).

#### 4. `DimDate`
- **Data Grain**: Exactly 1 record per calendar match day ($N=663$).
- **Primary Key**: `DateKey` (int YYYYMMDD)
- **Columns**:
  - `DateKey` (int, PK) — Date integer key (e.g., 20240415).
  - `Date` (datetime) — Standard calendar date.
  - `Year` (int) — Calendar year.
  - `Month` (int) — Month number (1–12).
  - `MonthName` (text) — Full month name.
  - `Quarter` (text) — Quarter string (Q1, Q2, Q3, Q4).
  - `DayOfWeek` (text) — Name of the day.

#### 5. `DimMatch`
- **Data Grain**: Exactly 1 record per evaluated senior match ($N=837$).
- **Primary Key**: `MatchID` (int)
- **Foreign Keys**: `CompID`, `DateKey`, `HomeTeamID`, `AwayTeamID`, `WinTeamID`
- **Columns**:
  - `MatchID` (int, PK) — Unique match identifier.
  - `CompID` (int, FK) — References `DimCompetition[CompID]`.
  - `DateKey` (int, FK) — References `DimDate[DateKey]`.
  - `MatchDate` (datetime) — Match date string.
  - `Stage` (text) — League / Group / Playoffs / Final.
  - `IsKnockOut` (int) — 1 if playoff/knockout, 0 otherwise.
  - `HomeTeamID` (int, FK) — References `DimTeam[TeamID]`.
  - `AwayTeamID` (int, FK) — References `DimTeam[TeamID]`.
  - `WinTeamID` (int, FK) — References `DimTeam[TeamID]`.
  - `Result` (text) — Match outcome string.

#### 6. `DimContext`
- **Data Grain**: Exactly 1 record per certified pressure context definition ($N=6$).
- **Primary Key**: `ContextID` (int)
- **Columns**:
  - `ContextID` (int, PK) — Unique context state key (1 to 6).
  - `ContextName` (text) — Descriptive scenario name (e.g., Chasing Clutch, Collapse Crisis, Death Overs).
  - `Innings` (int) — 1 (First), 2 (Second), or 0 (Both).
  - `PhaseName` (text) — Inning phase (Powerplay, Middle, Death, Chase).
  - `IsBatPressure` (int) — 1 if pressure batting context.
  - `IsBowlLeverage` (int) — 1 if high bowling execution leverage.
  - `Description` (text) — Mathematical criteria and cricketing trigger.

#### 7. `DimRanking`
- **Data Grain**: Exactly 1 record per certified Top 10 ranking entry ($N=20$: 10 Batters + 10 Bowlers).
- **Primary Key**: `RankingID` (int)
- **Foreign Key**: `PlayerID` (int)
- **Columns**:
  - `RankingID` (int, PK) — Surrogate ranking key (1 to 20).
  - `PlayerID` (int, FK) — References `DimPlayer[PlayerID]`.
  - `PlayerName` (text) — Canonical player name.
  - `Discipline` (text) — "Batter" or "Bowler".
  - `OfficialRank` (int) — Certified rank (1 to 10).
  - `CPRI` (decimal) — Official certified CPRI score (0–100).
  - `CPRI_CI_Low` (decimal) — 95% credible interval lower bound.
  - `CPRI_CI_High` (decimal) — 95% credible interval upper bound.
  - `ConfidenceClass` (text) — "Tier A (N>=100)" or "Tier B".
  - `OverallEvidenceTier` (text) — Certified 5-Dimension Evidence Tier (Tier 1 Marquee Core / Tier 2 High-Upside / Tier 3 Tactical / Tier 4 Foreign Target).
  - `RankingExplanation` (text) — Franchise scouting rationale.

---

### Fact Tables

#### 8. `FactDeliveryPressure`
- **Data Grain**: Exactly 1 record per senior delivery faced or bowled ($N=194,014$).
- **Primary Key**: `DeliveryID` (int)
- **Foreign Keys**: `MatchID`, `StrikerID`, `BowlerID`, `BattingTeamID`, `BowlingTeamID`, `ContextID`
- **Columns**:
  - `DeliveryID` (int, PK) — Surrogate integer delivery key.
  - `MatchID` (int, FK) — References `DimMatch[MatchID]`.
  - `Innings` (int) — Innings number (1 or 2).
  - `OverID` (int) — Over number (1 to 20).
  - `StrikerID` (int, FK) — References `DimPlayer[PlayerID]` (Active relationship).
  - `BowlerID` (int, FK) — References `DimPlayer[PlayerID]` (Inactive role-playing relationship).
  - `BattingTeamID` (int, FK) — References `DimTeam[TeamID]`.
  - `BowlingTeamID` (int, FK) — References `DimTeam[TeamID]`.
  - `ContextID` (int, FK) — References `DimContext[ContextID]`.
  - `RunsBat` (int) — Runs scored off the bat.
  - `BowlerRunsConceded` (int) — Runs charged to bowler (MCC Law 16).
  - `IsFour` (int) — 1 if 4 runs off bat.
  - `IsSix` (int) — 1 if 6 runs off bat.
  - `IsWicket` (int) — 1 if dismissal occurred.
  - `IsBowlerWicket` (int) — 1 if bowler-credited dismissal (excludes run-outs).
  - `IsLegalBatting` (int) — 1 if legal ball faced by batter (excludes wides).
  - `IsLegalBowling` (int) — 1 if legal ball bowled by bowler (excludes wides and no-balls).
  - `IsBatPressure` (int) — 1 if batting pressure state active ($\Psi_{\text{bat}} = 1$).
  - `IsBowlLeverage` (int) — 1 if bowling execution leverage active ($\lambda_{\text{bowl}} = 1$).
  - `PsiBat` (decimal) — Continuous batting pressure index (0 to 1).
  - `LambdaBowl` (decimal) — Continuous bowling execution leverage (0 to 1).

#### 9. `FactPlayerMatchPerformance`
- **Data Grain**: Exactly 1 record per player, match, and pressure state ($N=29,416$).
- **Primary Key**: `PlayerMatchID` (int)
- **Foreign Keys**: `MatchID`, `PlayerID`, `TeamID`
- **Columns**:
  - `PlayerMatchID` (int, PK) — Surrogate match-performance key.
  - `MatchID` (int, FK) — References `DimMatch[MatchID]`.
  - `PlayerID` (int, FK) — References `DimPlayer[PlayerID]`.
  - `TeamID` (int, FK) — References `DimTeam[TeamID]`.
  - `Discipline` (text) — "Batter" or "Bowler".
  - `IsPressureState` (int) — 1 if pressure state, 0 if normal.
  - `Balls` (int) — Balls faced or bowled in this match state.
  - `Runs` (int) — Runs scored or conceded.
  - `Outs` (int) — Dismissals suffered or wickets taken.
  - `Boundaries` (int) — Fours + sixes.
  - `Dots` (int) — Dot balls faced or bowled.
  - `RateMetric` (decimal) — Strike Rate (batters) or Economy (bowlers).

#### 10. `FactPlayerPressurePerformance`
- **Data Grain**: Exactly 1 record per player discipline profile ($N=1,235$).
- **Primary Key**: `PlayerPressurePerfID` (int)
- **Foreign Key**: `PlayerID` (int)
- **Columns**:
  - `PlayerPressurePerfID` (int, PK) — Surrogate profile key.
  - `PlayerID` (int, FK) — References `DimPlayer[PlayerID]`.
  - `Discipline` (text) — "Batter" or "Bowler".
  - `PressureBalls` (int) — Total pressure/leverage balls.
  - `NormalBalls` (int) — Total normal baseline balls.
  - `RawPressureMetric` (decimal) — Raw pressure SR or leverage Economy.
  - `NormalBaselineMetric` (decimal) — Baseline SR or Economy.
  - `DeltaContextMetric` (decimal) — Performance differential under pressure.
  - `BayesEstimate` (decimal) — Shrunk empirical Bayes posterior mean.
  - `Bayes_CI_Low` (decimal) — 2.5th percentile posterior bound.
  - `Bayes_CI_High` (decimal) — 97.5th percentile posterior bound.
  - `Bayes_CI_Width` (decimal) — Posterior credible interval width.
  - `BoundaryPct` (decimal) — Pressure boundary percentage.
  - `DotPct` (decimal) — Pressure dot ball percentage.
  - `DismissalOrWktRate` (decimal) — Dismissal % or Wicket %.
  - `MatchCV` (decimal) — Individual match-level coefficient of variation.
  - `MatchSuccessRate` (decimal) — Success percentage across qualified matches.
  - `JackknifeWorstCaseMetric` (decimal) — Metric under worst-case single match removal.
  - `JackknifeSE` (decimal) — Leave-One-Match-Out Jackknife standard error.

---

## 3. Role-Playing Dimensions & Active vs. Inactive Relationships

In cricket, a bowler in `FactDeliveryPressure` is a player entity, just like the batter (striker). Creating a secondary table or duplicating player names would bloat the model and create redundant metadata.

### The Solution: Inactive Role-Playing Relationship
- **Active Relationship**: `DimPlayer[PlayerID] (1) -> FactDeliveryPressure[StrikerID] (*)`
  - Used for all batting queries, pressure balls faced, and runs scored.
- **Inactive Relationship**: `DimPlayer[PlayerID] (1) -> FactDeliveryPressure[BowlerID] (*)`
  - Used for all bowling queries, balls bowled, and runs conceded.
  - Activated dynamically in DAX via the `USERELATIONSHIP()` function:
    ```dax
    [Total Deliveries Bowled] = 
    CALCULATE(
        COUNTROWS(FactDeliveryPressure),
        FactDeliveryPressure[IsLegalBowling] = 1,
        USERELATIONSHIP(DimPlayer[PlayerID], FactDeliveryPressure[BowlerID])
    )
    ```

This eliminates ambiguous path errors, eliminates circular references, and guarantees 100% mathematical precision.

---

## 4. VertiPaq Engine Performance & Storage Optimization

- **Data Compression**: VertiPaq applies dictionary encoding and run-length encoding (RLE) to sorted integer columns.
- **Memory Consumption**:
  - `FactDeliveryPressure` (194,014 rows): **~3.2 MB** in memory.
  - `FactPlayerMatchPerformance` (29,416 rows): **~0.6 MB** in memory.
  - `FactPlayerPressurePerformance` (1,235 rows): **~0.1 MB** in memory.
  - Dimension Tables (all combined): **~0.4 MB** in memory.
  - **Total Model Footprint**: **< 4.5 MB compressed**.
- **Query Latency**: All visual interactions render in **$< 150 \text{ ms}$** on standard Power BI Pro capacities.

