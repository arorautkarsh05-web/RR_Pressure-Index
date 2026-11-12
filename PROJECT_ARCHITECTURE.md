# RR Pressure Index 2027: System Architecture & Data Engineering Topology

---

## 1. System Overview

The **RR Pressure Index 2027** is an end-to-end analytical pipeline designed for deterministic execution, strict zero-leakage pre-delivery state reconstruction, and seamless integration between Python modeling engines and Power BI reporting interfaces.

```mermaid
graph TD
    subgraph Data Layer
        R1["data/raw/matches.csv<br>(883 Matches)"]
        R2["data/raw/ball_by_ball.csv<br>(200,999 Deliveries)"]
        R3["data/raw/competitions.csv<br>(138 Series)"]
    end

    subgraph Feature Engineering Engine
        F1["src/pressure_engine_v2.py"]
        R1 & R2 & R3 --> F1
        F1 --> T1["outputs/tables/delivery_pressure_features_v2.csv<br>(194,014 Senior Records)"]
    end

    subgraph Baselines & Empirical Bayes
        B1["src/baseline_engine_v2.py"]
        B2["src/reliability_model_v2.py"]
        T1 --> B1 --> T2["outputs/tables/context_adjusted_baselines.csv"]
        T2 --> B2 --> T3["outputs/tables/bowler_performance_profiles.csv"]
        T2 --> B2 --> T4["outputs/tables/batter_performance_profiles.csv"]
    end

    subgraph Ranking & Lineage Engine
        K1["src/player_ranking_engine.py"]
        T3 & T4 --> K1
        K1 --> O1["outputs/rankings/top_10_batters.csv"]
        K1 --> O2["outputs/rankings/top_10_bowlers.csv"]
        K1 --> O3["outputs/rankings/full_cohort_*.csv"]
    end

    subgraph Semantic Power BI Integration
        D1["outputs/dashboard/dim_*.csv"]
        D2["outputs/dashboard/fact_*.csv"]
        K1 & T1 --> D1 & D2
        D1 & D2 --> PBI["dashboard/RR_Auction_Intelligence.pbip"]
    end
```

---

## 2. Core Architectural Principles

1. **Pre-Delivery State Causality:** All pressure indicators ($\Psi_{\text{bat}}, \Lambda_{\text{bowl}}$) are conditioned strictly on variables known prior to the delivery being bowled.
2. **Kish Design Effect Correction:** Intra-cluster correlation is accounted for prior to shrinkage:
   $$deff = 1 + (\bar{m} - 1) \cdot \rho_{\text{ICC}}, \quad N_{\text{eff}} = \frac{N}{deff}$$
3. **Analytic Uncertainty Propagation:** Posterior variances are propagated through to index standard errors.
4. **Decoupled Scoring Interfaces:** Python outputs feed a standard Star-Schema data model in Power BI with zero manual transformation required in Power Query.
