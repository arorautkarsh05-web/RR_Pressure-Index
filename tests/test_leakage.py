"""
Unit tests for data leakage, temporal causality, and look-ahead bias prevention.
"""

import pytest
import pandas as pd
from src.config import TABLES_DIR

@pytest.fixture(scope="module")
def feat_data():
    feat_file = TABLES_DIR / "delivery_pressure_features_v2.csv"
    return pd.read_csv(feat_file, low_memory=False)

def test_zero_duplicate_deliveries(feat_data):
    """Verify zero duplicate delivery records exist across the entire 194,014 rows."""
    dups = feat_data.duplicated(subset=["match_id", "innings", "innings_ball_num"]).sum()
    assert dups == 0, f"Found {dups} duplicate delivery records"

def test_innings_start_zero_leakage(feat_data):
    """Verify all 1,660 innings opening deliveries start with strictly zero prior statistics."""
    inn_starts = feat_data[feat_data["innings_ball_num"] == 1]
    assert len(inn_starts) == 1660
    assert (inn_starts["cum_runs_before"] == 0).all(), "cum_runs_before not 0 at start of innings"
    assert (inn_starts["cum_wickets_before"] == 0).all(), "cum_wickets_before not 0 at start of innings"
    assert (inn_starts["legal_balls_bowled"] == 0).all(), "legal_balls_bowled not 0 at start of innings"

def test_pre_delivery_cumulative_invariance(feat_data):
    """Verify for arbitrary delivery k, cum_runs_before strictly equals prior runs."""
    sample = feat_data[feat_data["match_id"] == 13511]
    inn1 = sample[sample["innings"] == 1]
    
    # Calculate expected cum runs
    expected_cum = inn1["team_runs"].cumsum() - inn1["team_runs"]
    assert (inn1["cum_runs_before"] == expected_cum).all(), "cum_runs_before contains current delivery outcome"
