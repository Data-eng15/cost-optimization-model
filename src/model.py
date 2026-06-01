"""
Ensemble model training, evaluation, and inference.

Architecture
------------
Classification (Human / Hybrid / AI)
  Base learners:
    1. XGBoost Classifier
    2. Decision Tree Classifier
    3. ANN  (MLPClassifier — 128→64→32, ReLU, Adam)
    4. Logistic Regression (linear baseline)
  Meta-learner:
    Logistic Regression trained on out-of-fold base-learner predictions
    (StackingClassifier with cv=5 passthrough=True)

Regression (profit_margin_pct)
  Base learners:
    1. XGBoost Regressor
    2. Decision Tree Regressor
    3. ANN  (MLPRegressor — 128→64→32, ReLU, Adam)
    4. Linear Regression (linear baseline)
  Meta-learner:
    Ridge Regression
    (StackingRegressor with cv=5 passthrough=True)

Each pipeline = ColumnTransformer → StackingEstimator.
Models and metadata are persisted to models/.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

import matplotlib
matplotlib.use("Agg")   # non-interactive backend for server environments
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.ensemble import StackingClassifier, StackingRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from xgboost import XGBClassifier, XGBRegressor

from config import (
    ANN_CLF_PARAMS, ANN_RGR_PARAMS,
    CLASS_LABELS, CV_FOLDS,
    DT_CLF_PARAMS, DT_RGR_PARAMS,
    META_CLF_PARAMS, META_RGR_PARAMS,
    METADATA_PATH, MODELS_DIR,
    SEED, VIZ_DIR,
    XGBOOST_CLF_PARAMS, XGBOOST_RGR_PARAMS,
)
from feature_engineering import build_preprocessor, get_feature_names, label_encoder
from utils import (
    classification_metrics, get_logger, regression_metrics,
    save_json, save_model,
)

log = get_logger(__name__)


# ---------------------------------------------------------------------------
# Model builders
# ---------------------------------------------------------------------------

def _clf_base_learners() -> list[Tuple[str, object]]:
    return [
        ("xgb",  XGBClassifier(**XGBOOST_CLF_PARAMS)),
        ("dt",   DecisionTreeClassifier(**DT_CLF_PARAMS)),
        ("ann",  MLPClassifier(**ANN_CLF_PARAMS)),
        ("lr",   LogisticRegression(**META_CLF_PARAMS)),
    ]


def _rgr_base_learners() -> list[Tuple[str, object]]:
    return [
        ("xgb",  XGBRegressor(**XGBOOST_RGR_PARAMS)),
        ("dt",   DecisionTreeRegressor(**DT_RGR_PARAMS)),
        ("ann",  MLPRegressor(**ANN_RGR_PARAMS)),
        ("lr",   LinearRegression()),
    ]


def build_clf_pipeline() -> Pipeline:
    stacking = StackingClassifier(
        estimators=_clf_base_learners(),
        final_estimator=LogisticRegression(**META_CLF_PARAMS),
        cv=CV_FOLDS,
        passthrough=True,   # meta-learner also sees original features
        n_jobs=-1,
    )
    return Pipeline([
        ("pre", build_preprocessor()),
        ("clf", stacking),
    ])


def build_rgr_pipeline() -> Pipeline:
    stacking = StackingRegressor(
        estimators=_rgr_base_learners(),
        final_estimator=Ridge(**META_RGR_PARAMS),
        cv=CV_FOLDS,
        passthrough=True,
        n_jobs=-1,
    )
    return Pipeline([
        ("pre", build_preprocessor()),
        ("rgr", stacking),
    ])


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train_classifier(X_train, y_train) -> Pipeline:
    log.info("Training classification ensemble (XGB + DT + ANN + LR → meta LR)…")
    pipe = build_clf_pipeline()
    pipe.fit(X_train, y_train)
    log.info("Classification ensemble trained.")
    return pipe


def train_regressor(X_train, y_train) -> Pipeline:
    log.info("Training regression ensemble (XGB + DT + ANN + LR → meta Ridge)…")
    pipe = build_rgr_pipeline()
    pipe.fit(X_train, y_train)
    log.info("Regression ensemble trained.")
    return pipe


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate_classifier(pipe: Pipeline, X, y_true, split: str = "val") -> dict:
    y_pred = pipe.predict(X)
    y_prob = pipe.predict_proba(X)
    metrics = classification_metrics(y_true, y_pred, y_prob)
    log.info(
        f"[{split}] accuracy={metrics['accuracy']:.3f}  "
        f"f1={metrics['f1']:.3f}  recall={metrics['recall']:.3f}"
    )
    return metrics


def evaluate_regressor(pipe: Pipeline, X, y_true, split: str = "val") -> dict:
    y_pred = pipe.predict(X)
    metrics = regression_metrics(y_true, y_pred)
    log.info(
        f"[{split}] MAPE={metrics['mape_pct']:.2f}%  "
        f"RMSE={metrics['rmse']:.2f}  R²={metrics['r2']:.3f}"
    )
    return metrics


# ---------------------------------------------------------------------------
# Base-learner breakdown (for interpretability / debugging)
# ---------------------------------------------------------------------------

def evaluate_base_learners(
    X_train, y_clf_train, y_rgr_train,
    X_val,   y_clf_val,   y_rgr_val,
) -> dict:
    """Train and score each base learner individually for comparison."""
    pre = build_preprocessor()
    pre.fit(X_train)
    Xtr = pre.transform(X_train)
    Xvl = pre.transform(X_val)

    results: dict = {"classification": {}, "regression": {}}

    # Classification
    clf_bases = [
        ("XGBoost",          XGBClassifier(**XGBOOST_CLF_PARAMS)),
        ("DecisionTree",     DecisionTreeClassifier(**DT_CLF_PARAMS)),
        ("ANN",              MLPClassifier(**ANN_CLF_PARAMS)),
        ("LogisticRegr",     LogisticRegression(**META_CLF_PARAMS)),
    ]
    for name, model in clf_bases:
        model.fit(Xtr, y_clf_train)
        preds = model.predict(Xvl)
        from sklearn.metrics import accuracy_score, f1_score
        results["classification"][name] = {
            "accuracy": round(float(accuracy_score(y_clf_val, preds)), 4),
            "f1":       round(float(f1_score(y_clf_val, preds, average="weighted", zero_division=0)), 4),
        }

    # Regression
    rgr_bases = [
        ("XGBoost",       XGBRegressor(**XGBOOST_RGR_PARAMS)),
        ("DecisionTree",  DecisionTreeRegressor(**DT_RGR_PARAMS)),
        ("ANN",           MLPRegressor(**ANN_RGR_PARAMS)),
        ("LinearRegr",    LinearRegression()),
    ]
    for name, model in rgr_bases:
        model.fit(Xtr, y_rgr_train)
        preds = model.predict(Xvl)
        m = regression_metrics(y_rgr_val, preds)
        results["regression"][name] = {k: round(v, 4) for k, v in m.items()}

    return results


# ---------------------------------------------------------------------------
# Feature importance
# ---------------------------------------------------------------------------

def extract_feature_importance(clf_pipe: Pipeline) -> dict[str, float]:
    """
    Extract XGBoost feature importances from inside the stacking pipeline.
    Returns {feature_name: importance} sorted descending.
    """
    pre   = clf_pipe.named_steps["pre"]
    stack = clf_pipe.named_steps["clf"]
    xgb   = dict(stack.named_estimators_)["xgb"]

    names = get_feature_names(pre)
    importances = xgb.feature_importances_
    # importances array length may differ from names if XGB saw transformed data
    n = min(len(names), len(importances))
    fi = {names[i]: float(importances[i]) for i in range(n)}
    return dict(sorted(fi.items(), key=lambda x: x[1], reverse=True))


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

def plot_confusion_matrix(metrics: dict, split: str = "test") -> Path:
    VIZ_DIR.mkdir(parents=True, exist_ok=True)
    cm = np.array(metrics["confusion_matrix"])
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=CLASS_LABELS, yticklabels=CLASS_LABELS, ax=ax,
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title(f"Confusion Matrix ({split})")
    fig.tight_layout()
    out = VIZ_DIR / "confusion_matrix.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    log.info(f"Saved → {out}")
    return out


def plot_feature_importance(fi: dict[str, float], top_n: int = 15) -> Path:
    VIZ_DIR.mkdir(parents=True, exist_ok=True)
    items  = list(fi.items())[:top_n]
    names  = [x[0] for x in items][::-1]
    values = [x[1] for x in items][::-1]

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.barh(names, values, color="#2196F3")
    ax.set_xlabel("Importance (XGBoost gain)")
    ax.set_title("Top Feature Importances — XGBoost Base Learner")
    ax.bar_label(bars, fmt="%.3f", padding=3, fontsize=8)
    fig.tight_layout()
    out = VIZ_DIR / "feature_importance.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    log.info(f"Saved → {out}")
    return out


# ---------------------------------------------------------------------------
# Persist artefacts
# ---------------------------------------------------------------------------

def save_artefacts(
    clf_pipe: Pipeline,
    rgr_pipe: Pipeline,
    clf_metrics: dict,
    rgr_metrics: dict,
    base_results: dict,
    fi: dict,
) -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    save_model(clf_pipe, MODELS_DIR / "xgboost_classifier.pkl")
    save_model(rgr_pipe, MODELS_DIR / "stacking_regressor.pkl")

    metadata = {
        "project":        "TCO Optimisation Model — Sprint One",
        "version":        "1.0.0",
        "created_at":     datetime.now(timezone.utc).isoformat(),
        "seed":           SEED,
        "ensemble": {
            "classifier": "StackingClassifier(XGB+DT+ANN+LR → LR meta)",
            "regressor":  "StackingRegressor(XGB+DT+ANN+LinearR → Ridge meta)",
        },
        "classification_metrics": clf_metrics,
        "regression_metrics":     rgr_metrics,
        "base_learner_breakdown": base_results,
        "feature_importance":     {k: round(v, 5) for k, v in fi.items()},
        "class_labels":           CLASS_LABELS,
        "label_encoding":         {label: int(i) for i, label in enumerate(label_encoder.classes_)},
    }
    save_json(metadata, METADATA_PATH)
    log.info(f"Metadata saved → {METADATA_PATH}")


# ---------------------------------------------------------------------------
# Full training run (called from CLI or notebooks)
# ---------------------------------------------------------------------------

def run_training(
    X_train, X_val, X_test,
    y_clf_train, y_clf_val, y_clf_test,
    y_rgr_train, y_rgr_val, y_rgr_test,
) -> Tuple[Pipeline, Pipeline, dict]:

    clf_pipe = train_classifier(X_train, y_clf_train)
    rgr_pipe = train_regressor(X_train, y_rgr_train)

    clf_val  = evaluate_classifier(clf_pipe, X_val,  y_clf_val,  "val")
    clf_test = evaluate_classifier(clf_pipe, X_test, y_clf_test, "test")
    rgr_val  = evaluate_regressor(rgr_pipe,  X_val,  y_rgr_val,  "val")
    rgr_test = evaluate_regressor(rgr_pipe,  X_test, y_rgr_test, "test")

    base_results = evaluate_base_learners(
        X_train, y_clf_train, y_rgr_train,
        X_val,   y_clf_val,   y_rgr_val,
    )

    fi = extract_feature_importance(clf_pipe)
    plot_feature_importance(fi)
    plot_confusion_matrix(clf_test, "test")

    sprint_eval = {
        "classification": {"val": clf_val, "test": clf_test},
        "regression":     {"val": rgr_val, "test": rgr_test},
    }
    from config import METRICS_DIR
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    save_json(sprint_eval, METRICS_DIR / "sprint_one_evaluation.json")

    save_artefacts(clf_pipe, rgr_pipe, clf_test, rgr_test, base_results, fi)

    return clf_pipe, rgr_pipe, sprint_eval


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------

def predict(clf_pipe: Pipeline, rgr_pipe: Pipeline, X: "pd.DataFrame") -> dict:
    """Return team recommendation and per-scenario profit margins."""
    clf_label_idx  = clf_pipe.predict(X)[0]
    clf_proba      = clf_pipe.predict_proba(X)[0]
    recommended    = label_encoder.inverse_transform([clf_label_idx])[0]

    # Predict profit margin for all three scenarios by overriding the pipeline
    # We use the trained regression model as-is; the margin already reflects
    # the synthesised cost model so we report the direct prediction.
    margin = float(rgr_pipe.predict(X)[0])

    return {
        "recommended_team":  recommended,
        "probabilities":     {label_encoder.classes_[i]: round(float(p), 4)
                              for i, p in enumerate(clf_proba)},
        "predicted_profit_margin_pct": round(margin, 2),
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from feature_engineering import load_and_split
    (X_train, X_val, X_test,
     y_clf_train, y_clf_val, y_clf_test,
     y_rgr_train, y_rgr_val, y_rgr_test) = load_and_split()

    run_training(
        X_train, X_val, X_test,
        y_clf_train, y_clf_val, y_clf_test,
        y_rgr_train, y_rgr_val, y_rgr_test,
    )
