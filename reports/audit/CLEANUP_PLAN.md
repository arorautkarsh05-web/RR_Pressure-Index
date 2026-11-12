# RR PRESSURE INDEX 2027: REPOSITORY CLEANUP & CONSOLIDATION PLAN
## Phase 10 Audit: Safe Artifact Pruning, Redundancy Elimination & Canonical Asset Hardening

**Audit Execution Timestamp:** 2026-11-12  
**Auditor:** Production Release Engineer & Technical Documentation Auditor  

---

## 1. Principles of Repository Hygiene

In strict adherence to Non-Negotiable Rules 6, 7, and 15:
- **Rule 6:** Never remove an important file without understanding its purpose.
- **Rule 7:** Never delete source code, datasets, or documentation simply to reduce repository size.
- **Rule 15:** Every modification must be documented.

Cleanup is executed using an **explicit allowlist**. Broad wildcard deletions (`rm -rf *`) are forbidden.

---

## 2. Inventory Classification & Action Plan

| Asset Category | Target Path / Pattern | Purpose / Investigation Finding | Action Required | Reproducibility |
| :--- | :--- | :--- | :---: | :---: |
| **G. Temporary Files** | `__pycache__/`, `*.pyc` | Python byte-code cache | **PRUNE VIA GITIGNORE** | Fully reproducible |
| **G. Temporary Files** | `.pytest_cache/` | Test runner cache | **PRUNE VIA GITIGNORE** | Fully reproducible |
| **G. Temporary Files** | `.ipynb_checkpoints/` | Jupyter autosave state | **PRUNE VIA GITIGNORE** | Fully reproducible |
| **G. OS Artifacts** | `Thumbs.db`, `desktop.ini`, `.DS_Store` | Windows/Mac metadata | **PRUNE VIA GITIGNORE** | Non-essential |
| **F. Duplicate File** | `dashboard/index.html` | Duplicate of `dashboard/html/index.html` | **RETAIN CANONICAL** (`dashboard/html/index.html`) | Canonical preserved |
| **F. Duplicate File** | `report/RR_PRESSURE_INDEX_2027_LATEST_CHANGES_REPORT.pdf` | Duplicate of root deliverable | **CONSOLIDATE TO ROOT** | Canonical in root |
| **A. Core Source** | `src/*.py`, `tests/*.py` | Production pipelines and unit test suite | **NEVER DELETE (RETAIN)** | Essential source |
| **B. Essential Data** | `data/raw/*.csv` | Source ball-by-ball & match registry | **NEVER DELETE (RETAIN)** | Immutable raw data |
| **C. Outputs** | `outputs/tables/*.csv`, `outputs/rankings/*.csv` | Certified feature store & official rankings | **NEVER DELETE (RETAIN)** | Analytical deliverable |
| **D. Documentation** | `README.md`, `reports/audit/*.md` | Technical audit and methodology manuals | **NEVER DELETE (RETAIN)** | Core governance |

---

## 3. Explicit Protection List (Never Deleted)

1. `data/raw/matches.csv` (883 matches)
2. `data/raw/ball_by_ball.csv` (200,999 deliveries)
3. `data/raw/competitions.csv`
4. `outputs/tables/delivery_pressure_features_v2.csv` (194,014 rows)
5. `outputs/rankings/top_10_batters.csv` & `outputs/rankings/top_10_bowlers.csv`
6. `dashboard/RR_Auction_Intelligence.pbip` & `dashboard/RR_Auction_Intelligence.Dataset/model.bim`
7. `reports/audit/*.md` (Independent audit reports)
8. `tests/test_*.py` (Automated pytest suite)
9. `src/run_full_pipeline.py` (Master pipeline)
10. `src/config.py` (Central configuration)
