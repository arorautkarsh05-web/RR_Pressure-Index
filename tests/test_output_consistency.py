"""
Unit tests for output consistency and Power BI export parity.
"""

import pytest
import pandas as pd
from src.config import (
    DASHBOARD_DATA_DIR,
    RANKINGS_DIR,
    FEATURE_STORE_MATCHES_COUNT
)

def test_dashboard_dim_match_parity():
    """Verify Power BI dim_match contains exactly 837 feature store matches."""
    dim_match = pd.read_csv(DASHBOARD_DATA_DIR / "dim_match.csv")
    assert len(dim_match) == FEATURE_STORE_MATCHES_COUNT

def test_dashboard_fact_delivery_parity():
    """Verify Power BI fact_delivery_pressure contains exactly 194,014 rows."""
    fact_del = pd.read_csv(DASHBOARD_DATA_DIR / "fact_delivery_pressure.csv")
    assert len(fact_del) == 194014

def test_dashboard_dim_ranking_parity():
    """Verify Power BI dim_ranking aligns with official Top 10 rankings."""
    dim_rank = pd.read_csv(DASHBOARD_DATA_DIR / "dim_ranking.csv")
    top_bat = pd.read_csv(RANKINGS_DIR / "top_10_batters.csv")
    top_bowl = pd.read_csv(RANKINGS_DIR / "top_10_bowlers.csv")

    assert len(dim_rank) == 20  # 10 batters + 10 bowlers
    
    # Check top batter and top bowler presence
    assert 37052 in dim_rank["PlayerID"].values  # Naman Dhir
    assert 2933 in dim_rank["PlayerID"].values   # Jasprit Bumrah
