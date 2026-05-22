"""
Feature engineering pipeline — unified Greenfield + Legacy.

ColumnTransformer layout
------------------------
  project_type          → PassThrough (already 0/1)
  NUMERIC_FEATURES      → StandardScaler
  ORDINAL_FEATURES      → OrdinalEncoder (rank-preserving)
  BINARY_FEATURES       → PassThrough
  NOMINAL_FEATURES      → OneHotEncoder (drop='first')
  LEGACY_NUMERIC_FEATURES  → StandardScaler (Greenfield rows have 0-filled defaults)
  LEGACY_ORDINAL_FEATURES  → OrdinalEncoder

Greenfield records have legacy-specific columns filled with domain-sensible
defaults at synthesis time, so no imputation is needed — the model learns that
project_type=0 + default values = Greenfield context.
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import (
    LabelEncoder, OrdinalEncoder, OneHotEncoder, StandardScaler,
)
from sklearn.pipeline import Pipeline

from config import (
    ALL_FEATURES, BINARY_FEATURES, CLASS_LABELS, DATASET_PATH,
    DOMAIN_CATEGORIES, LEGACY_NUMERIC_FEATURES, LEGACY_ORDINAL_FEATURES,
    NOMINAL_FEATURES, NUMERIC_FEATURES, ORDINAL_FEATURES,
    PROJECT_TYPE_FEATURE, SEED, TARGET_CLASS, TARGET_REGR,
    TEST_SIZE, VAL_SIZE,
)
from utils import get_logger, validate_dataframe

log = get_logger(__name__)

# ---------------------------------------------------------------------------
# Label encoder (classification target)
# ---------------------------------------------------------------------------
label_encoder = LabelEncoder()
label_encoder.fit(CLASS_LABELS)   # Human=0, Hybrid=1, AI=2


# ---------------------------------------------------------------------------
# Column transformer
# ---------------------------------------------------------------------------

def _build_column_transformer() -> ColumnTransformer:
    ordinal_categories        = [ORDINAL_FEATURES[c]        for c in ORDINAL_FEATURES]
    legacy_ordinal_categories = [LEGACY_ORDINAL_FEATURES[c] for c in LEGACY_ORDINAL_FEATURES]

    return ColumnTransformer(
        transformers=[
            ("proj_type", "passthrough",
             PROJECT_TYPE_FEATURE),

            ("num",  StandardScaler(),
             NUMERIC_FEATURES),

            ("ord",  OrdinalEncoder(
                        categories=ordinal_categories,
                        handle_unknown="use_encoded_value",
                        unknown_value=-1,
                     ),
             list(ORDINAL_FEATURES.keys())),

            ("bin",  "passthrough",
             BINARY_FEATURES),

            ("nom",  OneHotEncoder(
                        categories=[DOMAIN_CATEGORIES],
                        drop="first",
                        handle_unknown="ignore",
                        sparse_output=False,
                     ),
             NOMINAL_FEATURES),

            ("leg_num", StandardScaler(),
             LEGACY_NUMERIC_FEATURES),

            ("leg_ord", OrdinalEncoder(
                        categories=legacy_ordinal_categories,
                        handle_unknown="use_encoded_value",
                        unknown_value=-1,
                        ),
             list(LEGACY_ORDINAL_FEATURES.keys())),
        ],
        remainder="drop",
    )


def build_preprocessor() -> ColumnTransformer:
    return _build_column_transformer()


# ---------------------------------------------------------------------------
# Load and split
# ---------------------------------------------------------------------------

def load_and_split(
    path: Path = DATASET_PATH,
) -> Tuple[
    pd.DataFrame, pd.DataFrame, pd.DataFrame,
    np.ndarray,   np.ndarray,   np.ndarray,
    np.ndarray,   np.ndarray,   np.ndarray,
]:
    df = pd.read_csv(path)
    log.info(f"Loaded dataset: {len(df)} records ({(df['project_type']==0).sum()} GF, "
             f"{(df['project_type']==1).sum()} Legacy) from {path}")

    X      = df[ALL_FEATURES].copy()
    y_clf  = label_encoder.transform(df[TARGET_CLASS].values)
    y_rgr  = df[TARGET_REGR].values.astype(float)

    X_tv, X_test, yc_tv, yc_test, yr_tv, yr_test = train_test_split(
        X, y_clf, y_rgr, test_size=TEST_SIZE, random_state=SEED, stratify=y_clf,
    )

    val_frac = VAL_SIZE / (1.0 - TEST_SIZE)
    X_train, X_val, yc_train, yc_val, yr_train, yr_val = train_test_split(
        X_tv, yc_tv, yr_tv, test_size=val_frac, random_state=SEED, stratify=yc_tv,
    )

    log.info(f"Split — train: {len(X_train)}, val: {len(X_val)}, test: {len(X_test)}")
    return X_train, X_val, X_test, yc_train, yc_val, yc_test, yr_train, yr_val, yr_test


# ---------------------------------------------------------------------------
# Feature names after transformation
# ---------------------------------------------------------------------------

def get_feature_names(ct: ColumnTransformer) -> list[str]:
    names = (
        PROJECT_TYPE_FEATURE
        + NUMERIC_FEATURES
        + list(ORDINAL_FEATURES.keys())
        + BINARY_FEATURES
        + [f"domain_{c}" for c in DOMAIN_CATEGORIES[1:]]   # OHE drop='first'
        + LEGACY_NUMERIC_FEATURES
        + list(LEGACY_ORDINAL_FEATURES.keys())
    )
    return names
