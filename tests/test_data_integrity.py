"""
Unit tests for data integrity and raw schema validation.
"""

import pytest
import pandas as pd
from src.config import (
    RAW_DATA_DIR,
    TABLES_DIR,
    RAW_MATCHES_COUNT,
    FEATURE_STORE_MATCHES_COUNT,
    EXCLUDED_EMERGING_TOURNAMENTS
)

def test_raw_files_exist():
    """Verify all required raw datasets exist on disk."""
    assert (RAW_DATA_DIR / "matches.csv").exists(), "matches.csv missing"
    assert (RAW_DATA_DIR / "ball_by_ball.csv").exists(), "ball_by_ball.csv missing"
    assert (RAW_DATA_DIR / "competitions.csv").exists(), "competitions.csv missing"

def test_raw_match_counts():
    """Verify total match count matches audited database layer."""
    df_matches = pd.read_csv(RAW_DATA_DIR / "matches.csv")
    assert len(df_matches) == RAW_MATCHES_COUNT, f"Expected {RAW_MATCHES_COUNT} matches, got {len(df_matches)}"
    assert df_matches["match_id"].nunique() == RAW_MATCHES_COUNT, "Duplicate match_ids found in matches.csv"

def test_senior_tournament_filtering():
    """Verify senior tournament population of 853 matches."""
    df_matches = pd.read_csv(RAW_DATA_DIR / "matches.csv")
    df_comp = pd.read_csv(RAW_DATA_DIR / "competitions.csv")
    m = df_matches.merge(df_comp, on="comp_id", how="left")
    
    # Exclude emerging tournaments
    senior_matches = m[~m["comp_name"].isin(EXCLUDED_EMERGING_TOURNAMENTS)]
    assert len(senior_matches) == 853, f"Expected 853 senior matches, got {len(senior_matches)}"

def test_feature_store_match_count():
    """Verify feature store contains exactly 837 matches with ball records."""
    feat_file = TABLES_DIR / "delivery_pressure_features_v2.csv"
    assert feat_file.exists(), "delivery_pressure_features_v2.csv missing"
    # Read unique match IDs
    df_feat_matches = pd.read_csv(feat_file, usecols=["match_id"])
    assert df_feat_matches["match_id"].nunique() == FEATURE_STORE_MATCHES_COUNT, (
        f"Expected {FEATURE_STORE_MATCHES_COUNT} matches, got {df_feat_matches['match_id'].nunique()}"
    )
