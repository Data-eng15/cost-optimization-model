# Model Architecture

## Problem Formulation

The TCO Optimisation Model solves two simultaneous prediction tasks from the same feature set:

1. **Classification**: Predict optimal team composition label — `Human`, `Hybrid`, or `AI`
2. **Regression**: Predict expected profit margin under the recommended configuration

Both tasks use a **Stacking Ensemble** architecture where multiple diverse base learners train in parallel and a meta-learner combines their predictions.

---

## Why Stacking?

Stacking outperforms simple voting or averaging because:
- The meta-learner learns **when to trust each base learner** — e.g., XGBoost is highly reliable for projects with strong ordinal signals, while the ANN better captures non-linear interaction effects.
- Diversity of base learners reduces variance. XGBoost, Decision Tree, ANN, and Linear models make different error types on different sub-regions of the feature space.
- `passthrough=True` gives the meta-learner access to original features alongside base-learner predictions, enabling corrective signals on cases where all base learners agree but are wrong.

---

## Classification Ensemble

### Base Learners

| Model | Params | Role |
|---|---|---|
| XGBoost Classifier | 300 trees, depth=5, lr=0.05, subsample=0.8 | Primary gradient-boosted ensemble; handles feature interactions, outliers, and mixed feature types naturally |
| Decision Tree Classifier | max_depth=6, min_samples_leaf=4, class_weight=balanced | Interpretable baseline; provides orthogonal decision boundaries to XGBoost |
| ANN (MLPClassifier) | 128→64→32, ReLU, Adam, α=0.001, early_stopping | Non-linear pattern capture; particularly effective for interaction effects between security/compliance features |
| Logistic Regression | C=1.0 | Linear baseline; calibrated probabilities; anchors meta-learner against overfitting |

### Meta-Learner

**Logistic Regression** (`C=1.0`) trained on 5-fold cross-validated out-of-fold predictions from all four base learners plus original features (`passthrough=True`).

**Why Logistic Regression as meta-learner?**
- Probability calibration: produces well-calibrated class probabilities
- Regularisation: prevents meta-learner from overfitting to base-learner noise
- Speed: fast convergence even with the augmented feature space from passthrough

### Performance (Sprint One, Test Set)
- **Accuracy: 93.3%** (NFR-01 target: ≥85% ✓)
- **F1: 93.4%** (weighted)
- **Recall: 93.3%** (NFR-05: maximised ✓)

---

## Regression Ensemble

### Base Learners

| Model | Params | Role |
|---|---|---|
| XGBoost Regressor | 300 trees, depth=4, lr=0.05, subsample=0.8 | Primary regressor; captures non-linear cost interactions |
| Decision Tree Regressor | max_depth=6, min_samples_leaf=4 | Piecewise-constant baseline; captures sharp feature thresholds |
| ANN (MLPRegressor) | 128→64→32, ReLU, Adam, α=0.001, early_stopping | Smooth non-linear function approximation |
| Linear Regression | — | Linear baseline; prevents ensemble from overfitting on noisy records |

### Meta-Learner

**Ridge Regression** (`α=1.0`) trained on 5-fold cross-validated out-of-fold predictions plus original features.

**Why Ridge as meta-learner?**
- L2 regularisation controls for multicollinearity between base learner predictions (XGBoost and DT are correlated)
- No hyperparameter search needed — α=1.0 is a sensible prior for normalised predictions

### Performance (Sprint One, Test Set)
- **MAPE: 3.48%** (NFR-02 target: ≤5% ✓)
- **RMSE: 1.65%**
- **R²: 0.972**

---

## Preprocessing Pipeline

```
Raw input DataFrame (15 features)
        │
        ▼
ColumnTransformer
  ├── StandardScaler     → 5 numeric features
  ├── OrdinalEncoder     → 8 ordinal features (rank-preserving)
  ├── PassThrough        → 1 binary feature (regulatory_compliance)
  └── OneHotEncoder(drop='first') → 1 nominal feature → 4 columns
        │
        ▼
18-feature transformed matrix
        │
        ▼
StackingClassifier / StackingRegressor
        │
        ▼
Prediction
```

---

## Why Not Deep Learning?

XGBoost and ANN (sklearn MLP) are the correct choices for this problem:

1. **Data type**: Structured tabular features, not images/text/audio
2. **Dataset size**: 800 records — insufficient for deep learning generalisation
3. **Interpretability**: Feature importance from XGBoost is a hard requirement (FR-20). Deep learning black-box models do not satisfy this.
4. **Training overhead**: PyTorch/Keras require GPU infrastructure and significantly more tuning. sklearn MLP achieves comparable non-linear modelling on tabular data with zero overhead.
5. **Industry benchmark**: LightGBM, XGBoost, and CatBoost consistently outperform deep learning on structured tabular data (Shwartz-Ziv & Armon, 2022).

---

## Serialisation

Models are serialised with `joblib` to:
- `models/xgboost_classifier.pkl` — full sklearn Pipeline (preprocessing + StackingClassifier)
- `models/random_forest_classifier.pkl` — full sklearn Pipeline (preprocessing + StackingRegressor)

Both pipelines are self-contained: the preprocessor is fitted and stored inside the pipeline, so inference requires only the input DataFrame — no separate preprocessing step.

---

## Inference Contract

**Input**: 15 raw SRS features (see `config.py:ALL_FEATURES`)
**Output**:
```json
{
  "recommended_team": "Hybrid",
  "probabilities": {"Human": 0.12, "Hybrid": 0.74, "AI": 0.14},
  "predicted_profit_margin_pct": 38.4
}
```

Inference time: < 1 second on local CPU hardware (NFR-03 target: ≤5s ✓).
