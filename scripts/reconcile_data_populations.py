"""
RR PRESSURE INDEX 2027 — DATA RECONCILIATION AUDIT SCRIPT
Investigates:
1. Match population discrepancies: 883 vs 853 vs 837.
2. Delivery accounting discrepancies: 186,540 vs 187,078, wides, no-balls, byes, leg-byes, penalty, runs, wickets.
Generates authoritative data and prints detailed diagnostics.
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path("D:/RR_PRESSURE_INDEX_2027")
RAW_DIR = BASE_DIR / "data" / "raw"

print("[*] Loading raw datasets...")
matches_df = pd.read_csv(RAW_DIR / "matches.csv")
bbb_df = pd.read_csv(RAW_DIR / "ball_by_ball.csv")
comp_df = pd.read_csv(RAW_DIR / "competitions.csv") if (RAW_DIR / "competitions.csv").exists() else None

print(f"Matches rows: {len(matches_df):,}")
print(f"Ball-by-ball rows: {len(bbb_df):,}")

# 1. Match Analysis
print("\n=== MATCH POPULATION ANALYSIS ===")
total_raw_matches = len(matches_df)
unique_raw_match_ids = matches_df["match_id"].nunique()
print(f"Total raw match records: {total_raw_matches}")
print(f"Unique match IDs in matches.csv: {unique_raw_match_ids}")

bbb_match_ids = set(bbb_df["match_id"].unique())
print(f"Unique match IDs in ball_by_ball.csv: {len(bbb_match_ids)}")

matches_without_deliveries = set(matches_df["match_id"]) - bbb_match_ids
print(f"Matches in matches.csv with 0 deliveries: {len(matches_without_deliveries)}")

# Merge competitions if available
if comp_df is not None and "competition_id" in matches_df.columns:
    m_comp = matches_df.merge(comp_df, on="competition_id", how="left")
    print("\nMatches by competition in matches.csv:")
    print(m_comp["competition_name"].value_counts(dropna=False))

# Check match status/results
if "result" in matches_df.columns or "status" in matches_df.columns:
    cols = [c for c in ["result", "status", "outcome", "match_type"] if c in matches_df.columns]
    print(f"\nMatch status breakdown for {cols}:")
    print(matches_df[cols].value_counts(dropna=False))

# Check date/season ranges
if "season" in matches_df.columns or "match_date" in matches_df.columns:
    date_col = "match_date" if "match_date" in matches_df.columns else "season"
    print(f"\nMatch date/season range in matches.csv: {matches_df[date_col].min()} to {matches_df[date_col].max()}")

# 2. Delivery Accounting in ball_by_ball.csv
print("\n=== DELIVERY ACCOUNTING IN RAW BALL_BY_BALL.CSV ===")
print("Columns in ball_by_ball.csv:", list(bbb_df.columns))

total_records = len(bbb_df)
print(f"Total delivery records: {total_records:,}")

# Look at match subset: all vs 853 senior vs 837 completed
# Check which matches have deliveries
balls_per_match = bbb_df.groupby("match_id").size()
print(f"Matches with deliveries: {len(balls_per_match)}")
print(f"Min balls in a match: {balls_per_match.min()}, Max: {balls_per_match.max()}, Median: {balls_per_match.median()}")

# Let's inspect extras columns
extra_cols = [c for c in bbb_df.columns if "wide" in c.lower() or "noball" in c.lower() or "bye" in c.lower() or "penalty" in c.lower() or "extra" in c.lower()]
print(f"Extras columns detected: {extra_cols}")

# Inspect runs columns
run_cols = [c for c in bbb_df.columns if "run" in c.lower() or "score" in c.lower()]
print(f"Run columns detected: {run_cols}")

# Inspect wicket columns
wkt_cols = [c for c in bbb_df.columns if "wicket" in c.lower() or "dismiss" in c.lower() or "out" in c.lower()]
print(f"Wicket columns detected: {wkt_cols}")
