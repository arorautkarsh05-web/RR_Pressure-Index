"""
Deep investigation into delivery accounting in the 837 senior matches (194,014 deliveries):
- Legal deliveries faced by batter (186,540 vs 187,078?)
- Legal deliveries bowled by bowler
- Wides, no-balls, legbyes, byes, penalty, other
- Runs: batter runs, total runs, bowler-conceded runs
- Wickets: total dismissals, bowler-credited wickets
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path("D:/RR_PRESSURE_INDEX_2027")
feat_file = BASE_DIR / "outputs" / "tables" / "delivery_pressure_features_v2.csv"
feat_df = pd.read_csv(feat_file)

print(f"Total deliveries in feature store: {len(feat_df):,}")
print("Columns in feature store:", list(feat_df.columns))

# Let's inspect the flags in feat_df
for col in ["is_legal_delivery", "is_legal", "legal_ball", "is_wide", "is_noball", "extras_type", "is_wicket"]:
    if col in feat_df.columns:
        print(f"\nValue counts for {col}:")
        print(feat_df[col].value_counts(dropna=False))

# Now let's inspect raw ball_by_ball for these 837 matches
raw_bbb = pd.read_csv(BASE_DIR / "data" / "raw" / "ball_by_ball.csv")
raw_senior = raw_bbb[raw_bbb["match_id"].isin(feat_df["match_id"].unique())]

print("\n=== RAW SENIOR DELIVERY ACCOUNTING (194,014 rows) ===")
print("extras_type in raw senior:")
print(raw_senior["extras_type"].value_counts(dropna=False))

# Look at extras1_runs and extras_2_runs
print("\nextras1_runs summary by extras_type:")
print(raw_senior.groupby("extras_type")["extras1_runs"].agg(["count", "sum", "unique"]))

if "extras_2_runs" in raw_senior.columns:
    print("\nextras_2_runs summary by extras_type:")
    print(raw_senior.groupby("extras_type")["extras_2_runs"].agg(["count", "sum", "unique"]))

# Check definitions of legal balls:
# 1. Batting legal balls: A wide is NOT a legal delivery faced by a batter.
# Are no-balls faced by the batter? Under MCC Law 21, a no-ball IS a delivery faced by the batter (batter can score runs off the bat).
# If batting legal ball = delivery where extras_type != 'wide':
batting_legal_no_wide = (raw_senior["extras_type"] != "wide").sum()
print(f"\nBatting legal balls (excluding wides only): {batting_legal_no_wide:,}")

# What if 'other' extras or penalty are excluded?
batting_legal_excl_wide_penalty = (~raw_senior["extras_type"].isin(["wide", "Penalty"])).sum()
print(f"Batting legal balls (excluding wide & penalty): {batting_legal_excl_wide_penalty:,}")

# What if no-ball is ALSO excluded from batting legal balls?
batting_legal_excl_wide_noball = (~raw_senior["extras_type"].isin(["wide", "Overstep"])).sum()
print(f"Batting legal balls (excluding wide & Overstep/noball): {batting_legal_excl_wide_noball:,}")

# What if 'other' has wides or noballs?
print("\nUnique values of 'stroke' or runs when extras_type == 'other':")
other_df = raw_senior[raw_senior["extras_type"] == "other"]
print(other_df[["runs", "extras1_runs", "extras_2_runs"]].head(10))

# 2. Bowling legal balls: Wides and No-balls are NOT legal deliveries bowled.
bowling_legal = (~raw_senior["extras_type"].isin(["wide", "Overstep"])).sum()
print(f"\nBowling legal balls (excluding wide and Overstep): {bowling_legal:,}")

# 3. Where did 186,540 come from?
# 194,014 - 186,540 = 7,474!
# Notice: 7,474 IS THE EXACT NUMBER OF WIDES (wide = 7,474)!
# 194,014 - 7,474 = 186,540!
print(f"\nCHECK: 194,014 - 7,474 wides = {194014 - 7474:,}")
if 194014 - 7474 == 186540:
    print("[!!!] 186,540 is EXACTLY (194,014 total deliveries - 7,474 wides)!")

# Now where did 187,078 come from?
# 187,078 - 186,540 = 538!
# Let's search previous code/reports for 187,078 to see how it was defined!
