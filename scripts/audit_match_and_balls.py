"""
Deep dive into match counts (883 vs 867 vs 853 vs 837)
and delivery counts (200,999 vs 194,014 vs 187,078 vs 186,540)
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path("D:/RR_PRESSURE_INDEX_2027")
RAW_DIR = BASE_DIR / "data" / "raw"

matches_df = pd.read_csv(RAW_DIR / "matches.csv")
bbb_df = pd.read_csv(RAW_DIR / "ball_by_ball.csv")
comp_df = pd.read_csv(RAW_DIR / "competitions.csv") if (RAW_DIR / "competitions.csv").exists() else None

# Check competition info
if comp_df is not None:
    m = matches_df.merge(comp_df, on="comp_id", how="left")
else:
    m = matches_df

print("Competitions breakdown across 883 matches:")
print(m["comp_name"].value_counts(dropna=False))

# Check match IDs present in delivery_pressure_features_v2.csv
features_file = BASE_DIR / "outputs" / "tables" / "delivery_pressure_features_v2.csv"
if features_file.exists():
    feat_df = pd.read_csv(features_file, usecols=["match_id", "delivery_id"] if "delivery_id" in pd.read_csv(features_file, nrows=2).columns else ["match_id"])
    print(f"\nMatches in delivery_pressure_features_v2.csv: {feat_df['match_id'].nunique():,}")
    print(f"Deliveries in delivery_pressure_features_v2.csv: {len(feat_df):,}")
    feat_matches = set(feat_df["match_id"].unique())
else:
    feat_matches = set()

# Inspect matches with deliveries
bbb_matches = set(bbb_df["match_id"].unique())

print(f"\nTotal matches in matches.csv: {len(matches_df)}")
print(f"Total matches in ball_by_ball.csv: {len(bbb_matches)}")
if feat_matches:
    print(f"Total matches in processed feature store: {len(feat_matches)}")

# What matches are in bbb but not in features?
excluded_from_feat = bbb_matches - feat_matches
print(f"Matches in bbb but excluded from features: {len(excluded_from_feat)}")
if excluded_from_feat:
    ex_m = matches_df[matches_df["match_id"].isin(excluded_from_feat)]
    print("\nExcluded matches details:")
    print(ex_m[["match_id", "comp_id", "result"]].head(20))
    if comp_df is not None:
        ex_m = ex_m.merge(comp_df, on="comp_id", how="left")
        print(ex_m["comp_name"].value_counts(dropna=False))

# Now let's check completed matches (result != 'No Result' and result != 'Match Abandoned')
has_result = matches_df[~matches_df["result"].isin(["No Result", "Match Abandoned"])]
print(f"\nMatches with a decisive result (excluding Abandoned & No Result): {len(has_result)}")
has_result_with_balls = matches_df[(matches_df["match_id"].isin(bbb_matches)) & (~matches_df["result"].isin(["No Result", "Match Abandoned"]))]
print(f"Matches with balls AND decisive result: {len(has_result_with_balls)}")
if feat_matches:
    feat_with_result = matches_df[(matches_df["match_id"].isin(feat_matches)) & (~matches_df["result"].isin(["No Result", "Match Abandoned"]))]
    print(f"Feature matches with decisive result: {len(feat_with_result)}")

# Now check delivery types in ball_by_ball.csv:
print("\n=== DELIVERY BREAKDOWN ===")
print("extras_type values in raw ball_by_ball.csv:")
print(bbb_df["extras_type"].value_counts(dropna=False))

# Look at 194,014 subset
if feat_matches:
    bbb_feat = bbb_df[bbb_df["match_id"].isin(feat_matches)]
    print(f"\nDeliveries in raw bbb for the {len(feat_matches)} feature matches: {len(bbb_feat):,}")
    print("extras_type in the feature matches subset:")
    print(bbb_feat["extras_type"].value_counts(dropna=False))
