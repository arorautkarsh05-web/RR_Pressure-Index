# POWER BI DESKTOP IMPLEMENTATION & USER GUIDE
## RR AUCTION INTELLIGENCE 2027: Pressure Performance & Player Reliability Command Center

---

### Executive Overview & Purpose

This document provides complete, step-by-step engineering instructions for configuring, opening, and operating the **RR AUCTION INTELLIGENCE 2027** production analytics dashboard inside **Microsoft Power BI Desktop**. 

The solution implements an enterprise-grade **Star Schema** architecture specifically designed for the Rajasthan Royals analytics department during the IPL 2027 mega-auction. It delivers sub-85 ms visual rendering, zero circular model relationships, strict empirical Bayes shrinkage, and certified data integrity across 194,014 Senior T20 deliveries (2022–2026).

---

## 1. System Requirements & Prerequisites

| Component | Minimum Specification | Recommended Specification |
|---|---|---|
| **Software** | Microsoft Power BI Desktop (October 2023 or newer) | Microsoft Power BI Desktop (Latest 64-bit Edition) |
| **Operating System** | Windows 10 (64-bit) / Windows 11 | Windows 11 Enterprise (64-bit) |
| **Processor** | 4-Core Intel Core i5 / AMD Ryzen 5 | 8-Core Intel Core i7 / AMD Ryzen 7 or higher |
| **System Memory (RAM)** | 8 GB RAM | 16 GB or 32 GB RAM |
| **Display Resolution** | 1920 &times; 1080 (16:9 Aspect Ratio) | 2560 &times; 1440 or 4K Ultra HD (16:9 Canvas) |
| **Data Directory** | `D:\RR_PRESSURE_INDEX_2027\dashboard\data\` | Local SSD with read permissions |

---

## 2. Solution File Manifest

The dashboard deployment package includes all necessary assets in `D:\RR_PRESSURE_INDEX_2027\dashboard\`:

```
d:\RR_PRESSURE_INDEX_2027\dashboard\
├── data\                                # 10 Certified Star Schema CSV tables
│   ├── dim_player.csv                   # 891 players with roles, batting styles, bowling styles
│   ├── dim_match.csv                    # 837 matches (367 IPL, 470 T20I)
│   ├── dim_competition.csv              # Competition hierarchy and format metadata
│   ├── dim_team.csv                     # Franchise & national teams with abbreviations
│   ├── dim_context.csv                  # 4 innings-phase clusters with baseline expectations
│   ├── dim_date.csv                     # Calendar dimension (2022-01-01 to 2026-12-31)
│   ├── dim_ranking.csv                  # Official Phase 03 player rankings (Top 10 Bat / Bowl)
│   ├── fact_delivery_pressure.csv       # 194,014 ball-by-ball records with Psi and Lambda
│   ├── fact_player_match_performance.csv# 18,367 match-level performances for CV & consistency
│   └── fact_player_pressure_performance.csv # Aggregated pressure metrics with Bayesian shrinkage
├── theme.json                           # Official Rajasthan Royals Power BI visual theme
├── dax_measures.dax                     # Complete repository of 30+ certified DAX measures
├── DAX_Measures.md                      # DAX reference documentation with formatting strings
├── power_query_scripts.m                # Power Query (M) ETL scripts for automated ingestion
├── POWER_BI_MODEL_DOCUMENTATION.md      # Data model ERD, schema grain, and architecture spec
├── PAGE_LAYOUT_SPECIFICATION.md         # Wireframe layouts and visual coordinate mappings
├── html\                                # Offline interactive dashboard (CORS-free prototype)
│   ├── index.html                       # 6-page interactive command center
│   ├── assets\styles.css                # Rajasthan Royals branded styling
│   ├── assets\dashboard.js              # Pure SVG charting engine & dossier controller
│   └── data\data.js                     # Offline embedded JSON data bundle
├── exports\                             # High-resolution PDF executive reports
│   ├── executive_overview.pdf
│   ├── batting_intelligence.pdf
│   ├── bowling_intelligence.pdf
│   └── auction_intelligence.pdf
└── validation\                          # Model and data reconciliation audit reports
    ├── dashboard_metric_reconciliation.csv
    ├── dashboard_model_validation.csv
    └── dashboard_performance_report.md
```

---

## 3. Step-by-Step Power BI Desktop Setup

### Step 3.1: Data Ingestion via Power Query (M)

1. Launch **Microsoft Power BI Desktop**.
2. On the ribbon, select **Get Data** &rarr; **Blank Query**.
3. Open the **Advanced Editor** (Home &rarr; Advanced Editor).
4. Open `D:\RR_PRESSURE_INDEX_2027\dashboard\power_query_scripts.m`.
5. Copy each table section and paste into a separate Query:
   - Query 1: `DimPlayer`
   - Query 2: `DimMatch`
   - Query 3: `DimCompetition`
   - Query 4: `DimTeam`
   - Query 5: `DimContext`
   - Query 6: `DimDate`
   - Query 7: `DimRanking`
   - Query 8: `FactDeliveryPressure`
   - Query 9: `FactPlayerMatchPerformance`
   - Query 10: `FactPlayerPressurePerformance`
6. Verify that the file paths point to your local data folder: `D:\RR_PRESSURE_INDEX_2027\dashboard\data\*.csv`.
7. Click **Close & Apply** to load the data into the VertiPaq engine. Total load time is approximately 8–12 seconds.

---

### Step 3.2: Setting Up the Star Schema Relationships

Navigate to the **Model View** in Power BI Desktop and create the following relationships.

> [!IMPORTANT]
> All relationships are strictly **1-to-Many ($1:*$)** with **Single** cross-filter direction. Do NOT enable bi-directional filtering.

#### 1. Relationships to `FactDeliveryPressure`
| From (Dimension) | Column | To (Fact) | Column | Cardinality | State |
|---|---|---|---|---|---|
| `DimMatch` | `MatchID` | `FactDeliveryPressure` | `MatchID` | $1:*$ | **Active** |
| `DimPlayer` | `PlayerID` | `FactDeliveryPressure` | `StrikerID` | $1:*$ | **Active** (Batting) |
| `DimPlayer` | `PlayerID` | `FactDeliveryPressure` | `BowlerID` | $1:*$ | **Inactive** (Role-Playing Bowling) |
| `DimContext` | `ContextClusterID` | `FactDeliveryPressure` | `ContextClusterID` | $1:*$ | **Active** |
| `DimDate` | `DateKey` | `FactDeliveryPressure` | `DateKey` | $1:*$ | **Active** |

#### 2. Relationships to `FactPlayerPressurePerformance`
| From (Dimension) | Column | To (Fact) | Column | Cardinality | State |
|---|---|---|---|---|---|
| `DimPlayer` | `PlayerID` | `FactPlayerPressurePerformance` | `PlayerID` | $1:*$ | **Active** |
| `DimCompetition` | `CompetitionID` | `FactPlayerPressurePerformance` | `CompetitionID` | $1:*$ | **Active** |
| `DimRanking` | `RankingID` | `FactPlayerPressurePerformance` | `RankingID` | $1:*$ | **Active** |

#### 3. Relationships to `FactPlayerMatchPerformance`
| From (Dimension) | Column | To (Fact) | Column | Cardinality | State |
|---|---|---|---|---|---|
| `DimPlayer` | `PlayerID` | `FactPlayerMatchPerformance` | `PlayerID` | $1:*$ | **Active** |
| `DimMatch` | `MatchID` | `FactPlayerMatchPerformance` | `MatchID` | $1:*$ | **Active** |

---

### Step 3.3: Configuring the Role-Playing Inactive Relationship

The connection from `DimPlayer[PlayerID]` to `FactDeliveryPressure[BowlerID]` is intentionally set to **Inactive**.
This prevents circular model dependency and allows `DimPlayer` to act cleanly as both Striker and Bowler.

When computing bowling metrics, DAX activates this path dynamically using `USERELATIONSHIP()`:

```dax
Bowling Deliveries = 
CALCULATE(
    COUNTROWS(FactDeliveryPressure),
    USERELATIONSHIP(FactDeliveryPressure[BowlerID], DimPlayer[PlayerID])
)
```

---

### Step 3.4: Applying the Rajasthan Royals Theme

1. On the Power BI Desktop ribbon, click the **View** tab.
2. In the **Themes** gallery, click the dropdown arrow &rarr; **Browse for themes**.
3. Select `D:\RR_PRESSURE_INDEX_2027\dashboard\theme.json`.
4. Power BI will apply the dark navy canvas (`#070B19`), card background (`#111936`), Rajasthan Royals Pink primary accent (`#E81B84`), Royal Blue secondary accent (`#004BA0`), and gold highlights (`#FFB81C`).

---

### Step 3.5: Creating the Measure Table & Ingesting DAX

1. In Home ribbon, click **Enter Data** and name the new table `_Measures`.
2. Open `D:\RR_PRESSURE_INDEX_2027\dashboard\dax_measures.dax`.
3. Create each DAX measure inside `_Measures`.
4. Group measures into their designated Display Folders in Model View:
   - `01 Core Volume & Macro`
   - `02 Batting Pressure & Baselines`
   - `03 Bowling Pressure & Baselines`
   - `04 Composite Pressure Reliability Index (CPRI)`
   - `05 Bayesian Intervals & Uncertainty`
   - `06 Match Consistency & Stability`
   - `07 Evidence Tiers & Dynamic Labels`
   - `08 Head-to-Head Comparison`
   - `09 Format Transferability`

---

## 4. Building the 6 Dashboard Pages

Follow the exact layout coordinates specified in `D:\RR_PRESSURE_INDEX_2027\dashboard\PAGE_LAYOUT_SPECIFICATION.md`:

### Page 1: Executive Command Center (`1280 × 720` px)
- **Top Row (Y=80)**: 6 KPI Cards (`Qualified Batters`, `Qualified Bowlers`, `Senior T20 Matches`, `Senior Deliveries`, `Top Batting CPRI`, `Top Bowling CPRI`).
- **Middle Row (Y=210)**: 
  - Left: Bar Chart of Top 5 Batters (`DimPlayer[PlayerName]` on Y-axis, `[Batting CPRI]` on X-axis, with error bars from `[Batting CPRI CI Lower]` to `[Batting CPRI CI Upper]`).
  - Right: Bar Chart of Top 5 Bowlers (`DimPlayer[PlayerName]` on Y-axis, `[Bowling CPRI]` on X-axis, with error bars from `[Bowling CPRI CI Lower]` to `[Bowling CPRI CI Upper]`).
- **Lower Row (Y=440)**:
  - Left: Scatter Plot of Batting Normal SR vs. Pressure SR.
  - Right: Scatter Plot of Bowling Normal Econ vs. Leverage Econ.

### Page 2: Batting Intelligence (`1280 × 720` px)
- **Top Slicer Bar (Y=80)**: Tournament slicer (`DimCompetition[CompetitionType]`), Evidence Tier (`DimRanking[EvidenceTier]`), Min Balls Faced.
- **Main Grid (Y=150)**:
  - Table Visual (Left 65%): `Rank`, `PlayerName`, `Batting CPRI`, `Pressure SR`, `Context Delta SR`, `Pressure Balls Faced`, `Bayes Shrunk SR`, `95% Credible Interval`, `Match CV`, `Evidence Tier`.
  - Player Dossier Card (Right 35%): Interactive detail card bound to selected player displaying role, sample breakdown, and auction scouting rationale.
- **Lower Panel (Y=520)**: Bayesian Credible Interval error bar visual.

### Page 3: Bowling Intelligence (`1280 × 720` px)
- **Top Slicer Bar (Y=80)**: Tournament slicer, Evidence Tier slicer, Min Balls Bowled.
- **Main Grid (Y=150)**:
  - Table Visual (Left 65%): `Rank`, `PlayerName`, `Bowling CPRI`, `Leverage Economy`, `Context Delta Econ`, `Pressure Balls Bowled`, `Bayes Shrunk Econ`, `95% Credible Interval`, `Match CV`, `Evidence Tier`.
  - Player Dossier Card (Right 35%): Interactive detail card for selected bowler.
- **Lower Panel (Y=520)**: Bayesian Credible Interval error bar visual.

### Page 4: Player Comparison Lab (`1280 × 720` px)
- **Top Controls (Y=80)**: Discipline selector, Player 1 (Benchmark) dropdown, Player 2 (Challenger) dropdown.
- **Matrix Visual (Y=160)**: Head-to-Head Comparison Matrix displaying CPRI, Pressure Metric, Delta, Volume, Credible Interval width, Match CV, and Jackknife stability.
- **Bottom Panels (Y=500)**: Tactical Fitment Analysis and Sensitivity commentary.

### Page 5: Auction Intelligence (`1280 × 720` px)
- **Top KPI Summary (Y=80)**: 4 Cards (`20 Targets`, `6 Tier 1 Core`, `8 Tier 2 High Ceiling`, `6 Tier 3 Strategic`).
- **Master Table (Y=170)**: 20-Player Combined Auction Board sorted by CPRI.
- **Strategy Cards (Y=510)**: 3 Cards for Acquisition Archetypes (Tier 1 Core, High-Ceiling Value, Tactical Specialists).

### Page 6: Model Methodology & Audit (`1280 × 720` px)
- 4 Documentation panels displaying mathematical formulas for $\Psi_{\text{bat}}$, $\lambda_{\text{bowl}}$, CPRI, and Star Schema reconciliation audit proofs.

---

## 5. Verification & Data Model Audit Checklist

Before presenting to the franchise executive board, verify:

- [x] Total Senior T20 Deliveries = **194,014**
- [x] Batting Legal Deliveries = **186,540**
- [x] Bowling Legal Deliveries = **185,715**
- [x] Wides = **7,474**, No-Balls = **825**
- [x] Evaluated Matches = **837** (367 IPL + 470 T20I)
- [x] Unique Evaluated Players = **891**
- [x] Qualified Batters (&ge;100 Pressure Balls) = **92**
- [x] Qualified Bowlers (&ge;120 Leverage Balls) = **167**
- [x] Top Batting CPRI = **Tim David (73.74)**
- [x] Top Bowling CPRI = **Jasprit Bumrah (72.24)**
- [x] Relationships = Zero many-to-many, zero circular paths
- [x] Memory footprint = **3.94 MB** in VertiPaq
- [x] Visual query execution = **<85 ms** across all visuals

---

## 6. Offline Interactive Prototype Alternative

For non-Power BI environments or instant browser demonstration, open:
`D:\RR_PRESSURE_INDEX_2027\dashboard\html\index.html`

The offline HTML prototype is completely standalone, requires zero web servers or internet connection, and provides identical interactivity, SVG charting, tab routing, and player dossier updates.

