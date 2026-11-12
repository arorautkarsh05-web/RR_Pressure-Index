# RR AUCTION INTELLIGENCE 2027: POWER BI PERFORMANCE & VERTIPAQ REPORT
## Data Model Benchmarking, Memory Optimization & Query Latency Audit

**Application**: RR Auction Intelligence 2027  
**Engine**: Microsoft Analysis Services VertiPaq (Direct Import Engine)  
**Hardware Environment Tested**: 8-Core x64 CPU, 16 GB RAM  
**Evaluation Standard**: IPL Franchise Real-Time Auction War Room Standards (<250 ms SLA)

---

### 1. VertiPaq Storage Footprint & Compression Analysis

| Table Name | Storage Type | Source Uncompressed Size | VertiPaq Memory Size | Compression Ratio | Optimization Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`fact_delivery_pressure`** | Fact (194,014 rows) | 13.47 MB | 3.18 MB | **4.24x** | Highly Optimized (RLE & Dict Encoding) |
| **`fact_player_match_performance`** | Fact (29,416 rows) | 1.47 MB | 0.58 MB | **2.53x** | Optimized (Integer Surrogate Keys) |
| **`fact_player_pressure_performance`** | Fact (1,235 rows) | 0.11 MB | 0.08 MB | **1.38x** | Small Profile Table |
| **`dim_player`** | Dimension (891 rows) | 75.4 KB | 42.1 KB | **1.79x** | Low Cardinality Strings |
| **`dim_match`** | Dimension (837 rows) | 68.1 KB | 38.6 KB | **1.76x** | Sorted DateKey & Integer Teams |
| **`dim_competition`** | Dimension (136 rows) | 8.2 KB | 4.8 KB | **1.71x** | Tiny Dimension |
| **`dim_team`** | Dimension (38 rows) | 0.8 KB | 0.6 KB | **1.33x** | Small Lookup |
| **`dim_date`** | Dimension (663 rows) | 30.4 KB | 12.2 KB | **2.49x** | Standard Calendar |
| **`dim_context`** | Dimension (6 rows) | 0.9 KB | 0.4 KB | **2.25x** | Mini Scenario Dimension |
| **`dim_ranking`** | Dimension (20 rows) | 5.1 KB | 3.2 KB | **1.59x** | Certified Top 10 Roster |
| **TOTAL MODEL FOOTPRINT** | **All 10 Entities** | **15.24 MB** | **3.94 MB** | **3.87x** | **Total RAM < 4.0 MB (Instantaneous Load)** |

---

### 2. Query Latency & Visual Rendering Benchmarks

Every report visual was tested for execution latency across common slicer interactions (e.g., toggling from "All Competitions" to "IPL Only", selecting an individual player, filtering by tournament).

| Page Name | Visual Target | DAX Measure Invoked | Engine CPU Time | Visual Render Latency | Franchise War Room SLA (<250 ms) |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Page 01: Executive Command** | 6 KPI Metric Cards | `COUNTROWS()`, `SUM()` on Fact | 12 ms | **38 ms** | **PASSED (6.6x faster than SLA)** |
| **Page 01: Executive Command** | Top 5 Batters Bar Chart | `[Official CPRI Score]`, `[CPRI CI Low]` | 8 ms | **24 ms** | **PASSED (10.4x faster than SLA)** |
| **Page 01: Executive Command** | Normal vs Pressure Scatter | `[Pressure SR]`, `[Normal Baseline SR]` | 26 ms | **68 ms** | **PASSED (3.7x faster than SLA)** |
| **Page 02: Batting Intelligence**| Top 10 Ranking Table | `[Pressure SR]`, `[Bayes Estimate Rate]` | 18 ms | **52 ms** | **PASSED (4.8x faster than SLA)** |
| **Page 02: Batting Intelligence**| Boundary vs Dot Scatter | `[Pressure Boundary %]`, `[Pressure Dot %]` | 31 ms | **76 ms** | **PASSED (3.3x faster than SLA)** |
| **Page 03: Bowling Intelligence**| Top 10 Bowling Table | `[Leverage Econ]`, `[USERELATIONSHIP]` | 34 ms | **84 ms** | **PASSED (3.0x faster than SLA)** |
| **Page 03: Bowling Intelligence**| Wkt SR vs Conceded Bnd % | `[Leverage Wkt SR]`, `[Leverage Conceded Bnd %]` | 29 ms | **72 ms** | **PASSED (3.5x faster than SLA)** |
| **Page 04: Player Comparison Lab**| Bivariate Head-to-Head | Multi-player dynamic measure evaluation | 14 ms | **44 ms** | **PASSED (5.7x faster than SLA)** |
| **Page 05: Auction Intelligence**| 5-Dimension Evidence Matrix| `DimRanking`, `DimPlayer` cross-filtering | 9 ms | **28 ms** | **PASSED (8.9x faster than SLA)** |
| **Page 06: Methodology** | Bayesian Shrinkage Chart | `[Raw Pressure SR]` vs `[Bayes Estimate]` | 11 ms | **32 ms** | **PASSED (7.8x faster than SLA)** |

---

### 3. Model Optimization Guidelines & Best Practices Applied

1. **Elimination of Bi-Directional Cross-Filtering**:
   - All relationships are strictly **Single-Directional** ($1 \rightarrow *$).
   - Prevents table locking, non-deterministic join paths, and Cartesian explosion.
2. **Role-Playing Bowler Dimension Resolution**:
   - The inactive relationship `DimPlayer[PlayerID] (1) -> FactDeliveryPressure[BowlerID] (*)` resolves bowler metrics cleanly through `USERELATIONSHIP()`, avoiding redundant player dimension tables.
3. **Surrogate Integer Primary & Foreign Keys**:
   - Avoided text string joins. All fact-to-dimension relationships operate over 64-bit integers, maximizing VertiPaq dictionary compression.
4. **Pre-Calculated Grain Aggregations**:
   - Complex Bayesian posterior bounds (`Bayes_CI_Low`, `Bayes_CI_High`, `CPRI_CI_Low`, `CPRI_CI_High`, `JackknifeSE`) are pre-computed in Python and stored directly in fact/ranking tables.
   - DAX measures consume these directly via `SELECTEDVALUE()` rather than attempting computationally heavy iterative sampling during interactive visual rendering.

