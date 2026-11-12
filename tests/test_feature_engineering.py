"""
Unit tests for feature engineering, pressure indices, and context par baselines.
"""

import pytest
import pandas as pd
import numpy as np
from src.config import TABLES_DIR, PSI_BAT_PRESSURE_THRESHOLD, LAMBDA_BOWL_LEVERAGE_THRESHOLD

@pytest.fixture(scope="module")
def feat_data():
    feat_file = TABLES_DIR / "delivery_pressure_features_v2.csv"
    return pd.read_csv(feat_file, low_memory=False)

def test_pressure_metric_bounds(feat_data):
    """Verify Psi_bat and Lambda_bowl are bounded in [0, 1]."""
    assert feat_data["psi_bat"].min() >= 0.0, "psi_bat has negative values"
    assert feat_data["psi_bat"].max() <= 1.0001, "psi_bat exceeds 1.0"
    assert feat_data["lambda_bowl"].min() >= 0.0, "lambda_bowl has negative values"
    assert feat_data["lambda_bowl"].max() <= 1.0001, "lambda_bowl exceeds 1.0"

def test_pressure_flag_alignment(feat_data):
    """Verify boolean pressure flags align with mathematical thresholds."""
    bat_press_expected = (feat_data["psi_bat"] >= PSI_BAT_PRESSURE_THRESHOLD).astype(int)
    assert (feat_data["is_bat_pressure"] == bat_press_expected).all(), "is_bat_pressure flag mismatch"

    bowl_lev_expected = (feat_data["lambda_bowl"] >= LAMBDA_BOWL_LEVERAGE_THRESHOLD).astype(int)
    assert (feat_data["is_bowl_leverage"] == bowl_lev_expected).all(), "is_bowl_leverage flag mismatch"

def test_cumulative_state_monotonicity(feat_data):
    """Verify cumulative runs and balls do not decrease within an innings."""
    # Test sample of matches
    sample_matches = feat_data["match_id"].unique()[:20]
    sample_df = feat_data[feat_data["match_id"].isin(sample_matches)]
    
    for (m_id, inn), group in sample_df.groupby(["match_id", "innings"]):
        runs_diff = group["cum_runs_before"].diff().dropna()
        balls_diff = group["legal_balls_bowled"].diff().dropna()
        assert (runs_diff >= 0).all(), f"cum_runs_before decreased in match {m_id} inn {inn}"
        assert (balls_diff >= 0).all(), f"legal_balls_bowled decreased in match {m_id} inn {inn}"
