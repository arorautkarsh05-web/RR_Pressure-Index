"""
Unit tests for Bayesian model calculations, conjugate empirical Bayes updates, and credible intervals.
"""

import pytest
import pandas as pd
import numpy as np
from src.config import TABLES_DIR, BOWLING_ICC_RHO, BATTING_ICC_RHO

@pytest.fixture(scope="module")
def bowler_profiles():
    return pd.read_csv(TABLES_DIR / "bowler_performance_profiles.csv")

@pytest.fixture(scope="module")
def batter_profiles():
    return pd.read_csv(TABLES_DIR / "batter_performance_profiles.csv")

def test_bumrah_bayesian_reproduction(bowler_profiles):
    """Verify Jasprit Bumrah's exact empirical Bayes posterior and credible interval."""
    bumrah = bowler_profiles[bowler_profiles["player_id"] == 2933].iloc[0]
    
    assert bumrah["pressure_balls"] == 763
    assert np.isclose(bumrah["raw_press_econ"], 6.9358, atol=1e-3)
    # Audited exact posterior: 7.1503
    assert np.isclose(bumrah["bayes_press_econ"], 7.1503, atol=1e-3)
    # 95% Credible interval bounds
    assert np.isclose(bumrah["bayes_econ_ci_low"], 6.30, atol=0.02)
    assert np.isclose(bumrah["bayes_econ_ci_high"], 8.00, atol=0.02)
    assert bumrah["bayes_econ_ci_width"] > 0

def test_naman_dhir_bayesian_reproduction(batter_profiles):
    """Verify Naman Dhir's exact empirical Bayes posterior and credible interval."""
    dhir = batter_profiles[batter_profiles["player_id"] == 37052].iloc[0]
    
    assert dhir["pressure_balls"] == 91
    assert np.isclose(dhir["raw_press_sr"], 215.3846, atol=1e-2)
    # Audited exact posterior: 195.15
    assert np.isclose(dhir["bayes_press_sr"], 195.15, atol=1e-1)
    # 95% Credible interval bounds
    assert np.isclose(dhir["bayes_sr_ci_low"], 158.97, atol=0.2)
    assert np.isclose(dhir["bayes_sr_ci_high"], 231.34, atol=0.2)

def test_credible_interval_consistency(batter_profiles, bowler_profiles):
    """Verify credible interval widths are positive and contain the posterior mean."""
    qual_bat = batter_profiles[batter_profiles["pressure_balls"] >= 50]
    for _, row in qual_bat.iterrows():
        assert row["bayes_sr_ci_low"] < row["bayes_press_sr"] < row["bayes_sr_ci_high"]
        assert row["bayes_sr_ci_width"] > 0

    qual_bowl = bowler_profiles[bowler_profiles["pressure_balls"] >= 60]
    for _, row in qual_bowl.iterrows():
        assert row["bayes_econ_ci_low"] < row["bayes_press_econ"] < row["bayes_econ_ci_high"]
        assert row["bayes_econ_ci_width"] > 0
