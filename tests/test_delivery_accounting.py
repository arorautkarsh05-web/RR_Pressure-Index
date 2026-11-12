"""
Unit tests for delivery accounting, legal-ball definitions, and extras reconciliation.
"""

import pytest
import pandas as pd
from src.config import TABLES_DIR, DASHBOARD_DATA_DIR

@pytest.fixture(scope="module")
def feat_data():
    feat_file = TABLES_DIR / "delivery_pressure_features_v2.csv"
    return pd.read_csv(feat_file, low_memory=False)

@pytest.fixture(scope="module")
def fact_data():
    fact_file = DASHBOARD_DATA_DIR / "fact_delivery_pressure.csv"
    return pd.read_csv(fact_file)

def test_total_delivery_count(feat_data, fact_data):
    """Verify total deliveries equal 194,014 across feature store and dashboard."""
    assert len(feat_data) == 194014
    assert len(fact_data) == 194014

def test_wides_and_noballs(feat_data):
    """Verify exact audited extras occurrences."""
    wides = (feat_data["extras_type"] == "wide").sum()
    noballs = (feat_data["extras_type"] == "Overstep").sum()
    assert wides == 7474, f"Expected 7,474 wides, got {wides}"
    assert noballs == 565, f"Expected 565 no-balls, got {noballs}"

def test_batting_legal_deliveries(feat_data, fact_data):
    """Verify batting legal balls equal 186,540 (Total - Wides)."""
    batting_legal = (feat_data["extras_type"] != "wide").sum()
    assert batting_legal == 186540, f"Expected 186,540 batting legal balls, got {batting_legal}"
    assert fact_data["IsLegalBatting"].sum() == 186540, "Dashboard IsLegalBatting mismatch"

def test_bowler_runs_and_wickets(feat_data, fact_data):
    """Verify run totals and wicket dismissals."""
    assert feat_data["runs"].sum() == 261119
    assert fact_data["RunsBat"].sum() == 261119
    assert feat_data["team_runs"].sum() == 269501
    assert feat_data["is_wicket"].sum() == 10486
    assert fact_data["IsWicket"].sum() == 10486
    assert feat_data["is_bowler_wicket"].sum() == 9905
    assert fact_data["IsBowlerWicket"].sum() == 9905
