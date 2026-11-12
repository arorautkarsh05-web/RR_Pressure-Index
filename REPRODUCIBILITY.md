# RR Pressure Index 2027: Deterministic Reproduction Guide

---

## 1. System Requirements & Prerequisites

- **Operating System:** Windows, macOS, or Linux
- **Python Version:** Python 3.10, 3.11, 3.12, or 3.13
- **Core Dependencies:**
  ```text
  pandas>=2.0.0
  numpy>=1.24.0
  scipy>=1.10.0
  scikit-learn>=1.2.0
  pytest>=7.0.0
  ```

---

## 2. Step-by-Step Reproduction Instructions

### Step 1: Clone Repository
```bash
git clone https://github.com/arorautkarsh05-web/RR_Pressure-Index.git
cd RR_Pressure-Index
```

### Step 2: Install Python Environment
```bash
python -m pip install --upgrade pip
pip install pandas numpy scipy scikit-learn pytest
```

### Step 3: Run Master Production Pipeline
```bash
python src/run_full_pipeline.py
```
*Expected Execution Time:* ~15–20 seconds.  
*Expected Output:* `PIPELINE COMPLETED SUCCESSFULLY in ~15.6 seconds.`

### Step 4: Run Automated Test Suite
```bash
python -m pytest tests/ -v
```
*Expected Output:* `23 passed in ~15s (100% pass rate)`.

---

## 3. Verifying Key Audited Outputs

After executing the pipeline, confirm numerical parity in Python:
```python
import pandas as pd
top_bowl = pd.read_csv("outputs/rankings/top_10_bowlers.csv")
print("Top Bowler:", top_bowl.iloc[0]["player_name"], "| CPRI:", top_bowl.iloc[0]["CPRI"])

top_bat = pd.read_csv("outputs/rankings/top_10_batters.csv")
print("Top Batter:", top_bat.iloc[0]["player_name"], "| CPRI:", top_bat.iloc[0]["CPRI"])
```
*Expected Outputs:*
- `Top Bowler: Jasprit Bumrah | CPRI: 76.83`
- `Top Batter: Naman Dhir | CPRI: 74.41`
