"""Helper functions: serialisation, validation, logging, metrics formatting."""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    f1_score, mean_absolute_percentage_error, mean_squared_error, r2_score,
    precision_score, recall_score,
)

from config import (
    ALL_FEATURES, BINARY_FEATURES, CLASS_LABELS, DOMAIN_CATEGORIES,
    GREENFIELD_LEGACY_DEFAULTS, LEGACY_NUMERIC_FEATURES, LEGACY_ORDINAL_FEATURES,
    MODELS_DIR, NOMINAL_FEATURES, NUMERIC_FEATURES, ORDINAL_FEATURES,
    TARGET_CLASS, TARGET_REGR,
)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s — %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

def save_model(model: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)


def load_model(path: Path) -> Any:
    return joblib.load(path)


def save_json(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=_json_serialiser)


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def _json_serialiser(obj: Any) -> Any:
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serialisable")


# ---------------------------------------------------------------------------
# Data validation
# ---------------------------------------------------------------------------

def validate_dataframe(df: pd.DataFrame) -> list[str]:
    """Return list of validation errors; empty list means OK."""
    errors = []

    present = [c for c in ALL_FEATURES if c in df.columns]
    missing_vals = df[present].isnull().sum()
    for col, count in missing_vals.items():
        if count > 0:
            errors.append(f"Missing values in '{col}': {count}")

    for col in NUMERIC_FEATURES + LEGACY_NUMERIC_FEATURES:
        if col in df.columns and (df[col] < 0).any():
            errors.append(f"Negative values in numeric column '{col}'")

    all_ordinals = {**ORDINAL_FEATURES, **LEGACY_ORDINAL_FEATURES}
    for col, levels in all_ordinals.items():
        if col in df.columns:
            invalid = set(df[col].dropna().unique()) - set(levels)
            if invalid:
                errors.append(f"Unknown levels in '{col}': {invalid}")

    if "regulatory_compliance" in df.columns:
        invalid_bin = set(df["regulatory_compliance"].unique()) - {0, 1}
        if invalid_bin:
            errors.append(f"Binary column 'regulatory_compliance' has values outside {{0,1}}: {invalid_bin}")

    if "project_type" in df.columns:
        invalid_pt = set(df["project_type"].unique()) - {0, 1}
        if invalid_pt:
            errors.append(f"'project_type' must be 0 (Greenfield) or 1 (Legacy), got: {invalid_pt}")

    if "domain_category" in df.columns:
        invalid_dom = set(df["domain_category"].unique()) - set(DOMAIN_CATEGORIES)
        if invalid_dom:
            errors.append(f"Unknown domain categories: {invalid_dom}")

    if TARGET_CLASS in df.columns:
        invalid_labels = set(df[TARGET_CLASS].unique()) - set(CLASS_LABELS)
        if invalid_labels:
            errors.append(f"Unknown class labels in '{TARGET_CLASS}': {invalid_labels}")

    return errors


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def classification_metrics(y_true, y_pred, y_prob=None) -> dict:
    # y_true / y_pred may be integer-encoded; use integer labels for sklearn
    int_labels = list(range(len(CLASS_LABELS)))
    metrics = {
        "accuracy":  float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
        "recall":    float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
        "f1":        float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=int_labels).tolist(),
        "report": classification_report(
            y_true, y_pred,
            labels=int_labels,
            target_names=CLASS_LABELS,
            output_dict=True,
        ),
    }
    return metrics


def regression_metrics(y_true, y_pred) -> dict:
    mape = float(mean_absolute_percentage_error(y_true, y_pred)) * 100
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2   = float(r2_score(y_true, y_pred))
    return {"mape_pct": mape, "rmse": rmse, "r2": r2}


# ---------------------------------------------------------------------------
# Inference helper — single record dict → validated DataFrame
# ---------------------------------------------------------------------------

def record_to_dataframe(record: dict) -> pd.DataFrame:
    """
    Convert a raw input dict to a validated, fully-featured DataFrame row.
    For Greenfield records (project_type=0), legacy-specific columns are
    automatically filled with their domain defaults.
    """
    r = dict(record)
    # Auto-fill legacy defaults for greenfield submissions
    if r.get("project_type", 0) == 0:
        for col, val in GREENFIELD_LEGACY_DEFAULTS.items():
            r.setdefault(col, val)
    df = pd.DataFrame([r])
    errors = validate_dataframe(df)
    if errors:
        raise ValueError("Input validation failed:\n" + "\n".join(errors))
    return df[ALL_FEATURES]
