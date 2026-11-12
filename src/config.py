"""
RR PRESSURE INDEX 2027 — CENTRAL CONFIGURATION MODULE
Centralized paths, mathematical thresholds, hyperparameters, and logging utilities.
"""

from pathlib import Path
import os
import logging
from typing import Dict, Any

# =============================================================================
# 1. PATH CONFIGURATION (Pathlib based)
# =============================================================================
BASE_DIR = Path(os.environ.get("RR_BASE_DIR", Path(__file__).resolve().parent.parent))

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

OUTPUTS_DIR = BASE_DIR / "outputs"
TABLES_DIR = OUTPUTS_DIR / "tables"
RANKINGS_DIR = OUTPUTS_DIR / "rankings"
DASHBOARD_OUTPUT_DIR = OUTPUTS_DIR / "dashboard"
FINAL_SUBMISSION_DIR = OUTPUTS_DIR / "final_submission"

REPORTS_DIR = BASE_DIR / "reports"
AUDIT_DIR = REPORTS_DIR / "audit"

DASHBOARD_DIR = BASE_DIR / "dashboard"
DASHBOARD_DATA_DIR = OUTPUTS_DIR / "dashboard"

TESTS_DIR = BASE_DIR / "tests"

# Ensure essential output directories exist
for d in [TABLES_DIR, RANKINGS_DIR, DASHBOARD_OUTPUT_DIR, FINAL_SUBMISSION_DIR, AUDIT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# =============================================================================
# 2. POPULATION & MATCH FILTER THRESHOLDS
# =============================================================================
RAW_MATCHES_COUNT = 883
SENIOR_MATCHES_COUNT = 853
FEATURE_STORE_MATCHES_COUNT = 837
DECISIVE_MATCHES_COUNT = 813

EXCLUDED_EMERGING_TOURNAMENTS = [
    "Mens T20 Emerging Teams Asia Cup 2024",
    "Asia Cup Rising Stars 2025"
]

# =============================================================================
# 3. PRESSURE & LEVERAGE THRESHOLDS
# =============================================================================
PSI_BAT_PRESSURE_THRESHOLD = 0.55
LAMBDA_BOWL_LEVERAGE_THRESHOLD = 0.50

# =============================================================================
# 4. QUALIFICATION THRESHOLDS
# =============================================================================
BATTER_MIN_BALLS = 50       # Qualified cohort for official batting ranking
BOWLER_MIN_BALLS = 60       # Qualified cohort for official bowling ranking

BATTER_PRIOR_MIN_BALLS = 30  # Threshold to compute empirical prior distribution
BOWLER_PRIOR_MIN_BALLS = 40  # Threshold to compute empirical prior distribution

# =============================================================================
# 5. BAYESIAN EMPIRICAL SHRINKAGE & CLUSTERING HYPERPARAMETERS
# =============================================================================
BOWLING_ICC_RHO = 0.0159     # Delivery-level intra-cluster correlation across matches
BATTING_ICC_RHO = 0.0182     # Delivery-level intra-cluster correlation across matches

BOWLER_CLUSTER_CAP = 24.0   # Maximum average cluster size cap for Kish deff
BATTER_CLUSTER_CAP = 15.0   # Maximum average cluster size cap for Kish deff

RANDOM_SEED = 42

# CPRI Component Weights
CPRI_WEIGHTS: Dict[str, float] = {
    "delta_rate": 0.40,
    "boundary_pct": 0.30,
    "dot_pct": 0.15,
    "wicket_dismissal_pct": 0.15,
}

# =============================================================================
# 6. STRUCTURED LOGGING
# =============================================================================
def get_logger(name: str = "RR_PRESSURE_INDEX") -> logging.Logger:
    """Configures and returns a structured logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s | [%(levelname)s] | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
