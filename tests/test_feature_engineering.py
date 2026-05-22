"""Unit tests for feature_engineering.py"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import pandas as pd
import pytest

from feature_engineering import (
    build_preprocessor, get_feature_names, label_encoder, load_and_split,
)
from config import ALL_FEATURES, CLASS_LABELS, DATASET_PATH


class TestLabelEncoder:
    def test_classes(self):
        assert set(label_encoder.classes_) == set(CLASS_LABELS)

    def test_round_trip(self):
        encoded = label_encoder.transform(CLASS_LABELS)
        decoded = label_encoder.inverse_transform(encoded)
        assert list(decoded) == CLASS_LABELS


class TestPreprocessor:
    def test_build_runs(self):
        pre = build_preprocessor()
        assert pre is not None

    def test_fit_transform_shape(self):
        df = pd.read_csv(DATASET_PATH)
        X = df[ALL_FEATURES]
        pre = build_preprocessor()
        Xt = pre.fit_transform(X)
        # 1 project_type + 5 numeric + 8 ordinal + 1 binary
        # + 4 OHE (5 domain categories, drop first)
        # + 6 legacy numeric + 4 legacy ordinal = 29
        assert Xt.shape[1] == 29
        assert Xt.shape[0] == len(X)

    def test_no_nans_after_transform(self):
        df = pd.read_csv(DATASET_PATH)
        X = df[ALL_FEATURES]
        pre = build_preprocessor()
        Xt = pre.fit_transform(X)
        assert not np.isnan(Xt).any()

    def test_feature_names_length(self):
        pre = build_preprocessor()
        df = pd.read_csv(DATASET_PATH)
        pre.fit(df[ALL_FEATURES])
        names = get_feature_names(pre)
        assert len(names) == 29


class TestLoadAndSplit:
    def test_split_sizes(self):
        (X_tr, X_vl, X_te,
         yc_tr, yc_vl, yc_te,
         yr_tr, yr_vl, yr_te) = load_and_split()

        total = len(X_tr) + len(X_vl) + len(X_te)
        df    = pd.read_csv(DATASET_PATH)
        assert total == len(df)

    def test_y_clf_dtype(self):
        (X_tr, _, _,
         yc_tr, _, _,
         _, _, _) = load_and_split()
        assert yc_tr.dtype in (np.int32, np.int64, np.intp)

    def test_y_rgr_dtype(self):
        (_, _, _,
         _, _, _,
         yr_tr, _, _) = load_and_split()
        assert yr_tr.dtype == float

    def test_stratification(self):
        (X_tr, X_vl, X_te,
         yc_tr, yc_vl, yc_te,
         _, _, _) = load_and_split()
        # Each split should contain all 3 classes
        for y in (yc_tr, yc_vl, yc_te):
            assert len(set(y)) == 3
