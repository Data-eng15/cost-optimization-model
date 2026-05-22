"""Central configuration: paths, feature schema, hyperparameters."""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]

DATA_RAW        = ROOT / "data" / "raw" / "greenfield_srs"
DATA_PROCESSED  = ROOT / "data" / "processed"
DATA_SYNTHETIC  = ROOT / "data" / "synthetic"
MODELS_DIR      = ROOT / "models"
RESULTS_DIR     = ROOT / "results"
METRICS_DIR     = RESULTS_DIR / "metrics"
VIZ_DIR         = RESULTS_DIR / "visualizations"
PREDICTIONS_DIR = RESULTS_DIR / "predictions"

DATASET_PATH    = DATA_PROCESSED / "combined_features.csv"   # unified Greenfield + Legacy
METADATA_PATH   = MODELS_DIR / "model_metadata.json"

# ---------------------------------------------------------------------------
# Random seed — guarantees 100% reproducibility (NFR-07)
# ---------------------------------------------------------------------------
SEED = 42

# ---------------------------------------------------------------------------
# Dataset synthesis
# ---------------------------------------------------------------------------
N_SAMPLES          = 800   # records per project type
PROJECT_TYPES      = ["Greenfield", "Legacy"]

# ---------------------------------------------------------------------------
# Shared features (apply to both Greenfield and Legacy)
# ---------------------------------------------------------------------------
NUMERIC_FEATURES = [
    "estimated_loc",
    "timeline_days",
    "team_size_required",
    "integration_count",
    "testing_coverage_pct",
]

ORDINAL_FEATURES = {
    "complexity_score":     ["Low", "Medium", "High"],
    "technical_risk_level": ["Low", "Medium", "High", "Critical"],
    "seniority_required":   ["Junior", "Mid", "Senior", "Architect"],
    "documentation_level":  ["Minimal", "Standard", "Comprehensive"],
    "performance_tier":     ["Standard", "High", "Real-time"],
    "security_criticality": ["Low", "Medium", "High", "Critical"],
    "budget_pressure":      ["Flexible", "Moderate", "Tight"],
    "maintainability_req":  ["Low", "Medium", "High"],
}

BINARY_FEATURES  = ["regulatory_compliance"]
NOMINAL_FEATURES = ["domain_category"]
DOMAIN_CATEGORIES = ["Web", "Infrastructure", "Security", "Data", "Mobile"]

# ---------------------------------------------------------------------------
# Legacy-specific features
# Sprint Two adds these — Greenfield records receive sensible defaults so the
# unified model can be trained on a single combined DataFrame.
# ---------------------------------------------------------------------------
LEGACY_NUMERIC_FEATURES = [
    "codebase_age_years",           # 1–30
    "existing_test_coverage_pct",   # 0–80 (existing test suite quality)
    "dependency_count",             # 10–500
    "last_refactor_years",          # 0–15
    "incident_rate_monthly",        # production incidents per month 0–20
    "code_duplication_pct",         # % duplicated code 0–60
]

LEGACY_ORDINAL_FEATURES = {
    "technical_debt_score":  ["Low", "Medium", "High", "Critical"],
    "documentation_quality": ["Poor", "Minimal", "Standard", "Good"],
    "language_modernity":    ["Legacy", "Dated", "Modern", "Current"],
    "team_familiarity":      ["Unfamiliar", "Low", "Medium", "High"],
}

# Greenfield defaults for legacy-specific columns
GREENFIELD_LEGACY_DEFAULTS = {
    "codebase_age_years":         0,
    "existing_test_coverage_pct": 0.0,
    "dependency_count":           0,
    "last_refactor_years":        0,
    "incident_rate_monthly":      0.0,
    "code_duplication_pct":       0.0,
    "technical_debt_score":       "Low",
    "documentation_quality":      "Poor",
    "language_modernity":         "Current",
    "team_familiarity":           "High",   # greenfield team knows their own new codebase
}

# project_type binary: 0 = Greenfield, 1 = Legacy
PROJECT_TYPE_FEATURE = ["project_type"]

# ---------------------------------------------------------------------------
# Unified feature list (all models trained on this)
# ---------------------------------------------------------------------------
ALL_FEATURES = (
    PROJECT_TYPE_FEATURE
    + NUMERIC_FEATURES
    + list(ORDINAL_FEATURES.keys())
    + BINARY_FEATURES
    + NOMINAL_FEATURES
    + LEGACY_NUMERIC_FEATURES
    + list(LEGACY_ORDINAL_FEATURES.keys())
)

TARGET_CLASS  = "target_team_label"
TARGET_REGR   = "profit_margin_pct"
CLASS_LABELS  = ["Human", "Hybrid", "AI"]

# ---------------------------------------------------------------------------
# Train / validation / test split ratios
# ---------------------------------------------------------------------------
TEST_SIZE = 0.15
VAL_SIZE  = 0.15

# ---------------------------------------------------------------------------
# Model hyperparameters
# ---------------------------------------------------------------------------
XGBOOST_CLF_PARAMS = {
    "n_estimators":      300,
    "max_depth":         5,
    "learning_rate":     0.05,
    "subsample":         0.8,
    "colsample_bytree":  0.8,
    "min_child_weight":  3,
    "gamma":             0.1,
    "reg_alpha":         0.1,
    "reg_lambda":        1.0,
    "eval_metric":       "mlogloss",
    "random_state":      SEED,
    "n_jobs":            -1,
}

XGBOOST_RGR_PARAMS = {
    "n_estimators":      300,
    "max_depth":         4,
    "learning_rate":     0.05,
    "subsample":         0.8,
    "colsample_bytree":  0.8,
    "min_child_weight":  3,
    "gamma":             0.05,
    "reg_alpha":         0.1,
    "reg_lambda":        1.0,
    "random_state":      SEED,
    "n_jobs":            -1,
}

DT_CLF_PARAMS = {
    "max_depth":         6,
    "min_samples_split": 8,
    "min_samples_leaf":  4,
    "class_weight":      "balanced",
    "random_state":      SEED,
}

DT_RGR_PARAMS = {
    "max_depth":         6,
    "min_samples_split": 8,
    "min_samples_leaf":  4,
    "random_state":      SEED,
}

ANN_CLF_PARAMS = {
    "hidden_layer_sizes":  (128, 64, 32),
    "activation":          "relu",
    "solver":              "adam",
    "alpha":               0.001,
    "batch_size":          32,
    "learning_rate_init":  0.001,
    "max_iter":            500,
    "early_stopping":      True,
    "validation_fraction": 0.1,
    "n_iter_no_change":    20,
    "random_state":        SEED,
}

ANN_RGR_PARAMS = {
    "hidden_layer_sizes":  (128, 64, 32),
    "activation":          "relu",
    "solver":              "adam",
    "alpha":               0.001,
    "batch_size":          32,
    "learning_rate_init":  0.001,
    "max_iter":            500,
    "early_stopping":      True,
    "validation_fraction": 0.1,
    "n_iter_no_change":    20,
    "random_state":        SEED,
}

META_CLF_PARAMS = {"C": 1.0, "max_iter": 1000, "random_state": SEED}
META_RGR_PARAMS = {"alpha": 1.0}

CV_FOLDS = 5
