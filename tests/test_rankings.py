"""
Unit tests for player rankings, CPRI score generation, and cohort qualification.
"""

import pytest
import pandas as pd
import numpy as np
from src.config import RANKINGS_DIR

@pytest.fixture(scope="module")
def top_batters():
    return pd.read_csv(RANKINGS_DIR / "top_10_batters.csv")

@pytest.fixture(scope="module")
def top_bowlers():
    return pd.read_csv(RANKINGS_DIR / "top_10_bowlers.csv")

def test_top_10_batters_order_and_scores(top_batters):
    """Verify Top 10 Batters rank order and reference CPRI values."""
    assert len(top_batters) == 10
    assert list(top_batters["pressure_rank"]) == list(range(1, 11))
    
    # Leader: Naman Dhir
    leader = top_batters.iloc[0]
    assert leader["player_name"] == "Naman Dhir"
    assert leader["player_id"] == 37052
    assert np.isclose(leader["CPRI"], 74.41, atol=0.05)
    assert np.isclose(leader["cpri_ci_low"], 64.48, atol=0.1)
    assert np.isclose(leader["cpri_ci_high"], 84.34, atol=0.1)

    # Monotonic decreasing CPRI
    assert (top_batters["CPRI"].diff().dropna() <= 0).all(), "Batters CPRI is not monotonically decreasing"

def test_top_10_bowlers_order_and_scores(top_bowlers):
    """Verify Top 10 Bowlers rank order and reference CPRI values."""
    assert len(top_bowlers) == 10
    assert list(top_bowlers["pressure_rank"]) == list(range(1, 11))
    
    # Leader: Jasprit Bumrah
    leader = top_bowlers.iloc[0]
    assert leader["player_name"] == "Jasprit Bumrah"
    assert leader["player_id"] == 2933
    assert np.isclose(leader["CPRI"], 76.83, atol=0.05)
    assert np.isclose(leader["cpri_ci_low"], 70.24, atol=0.1)
    assert np.isclose(leader["cpri_ci_high"], 83.42, atol=0.1)

    # Monotonic decreasing CPRI
    assert (top_bowlers["CPRI"].diff().dropna() <= 0).all(), "Bowlers CPRI is not monotonically decreasing"

def test_confidence_tier_assignment(top_batters, top_bowlers):
    """Verify confidence tier assignment reflects sample sizes."""
    for _, row in top_batters.iterrows():
        if row["pressure_balls"] >= 100:
            assert "Tier A" in row["confidence_class"]
        else:
            assert "Tier B" in row["confidence_class"]

    for _, row in top_bowlers.iterrows():
        if row["pressure_balls"] >= 100:
            assert "Tier A" in row["confidence_class"]
        else:
            assert "Tier B" in row["confidence_class"]
