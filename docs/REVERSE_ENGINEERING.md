# TCO Optimisation Model — Complete Reverse-Engineering Reference

> Every concept, design decision, and data flow explained from scratch.  
> Audience: anyone picking up this repo cold.

---

## Table of Contents

1. [What the Project Does](#1-what-the-project-does)
2. [GitHub Version History](#2-github-version-history)
3. [Repository Layout](#3-repository-layout)
4. [The Problem Being Solved](#4-the-problem-being-solved)
5. [Data Synthesis — How Training Data Is Made](#5-data-synthesis)
6. [Feature Schema — All 29 Inputs](#6-feature-schema)
7. [Label Assignment Rules](#7-label-assignment-rules)
8. [NFR-06 Safety Gate](#8-nfr-06-safety-gate)
9. [Profit Margin Formula](#9-profit-margin-formula)
10. [Feature Engineering Pipeline](#10-feature-engineering-pipeline)
11. [Model Architecture — Stacking Ensemble](#11-model-architecture)
12. [Training & Evaluation](#12-training--evaluation)
13. [Model Performance](#13-model-performance)
14. [Inference Flow](#14-inference-flow)
15. [Frontend Dashboard](#15-frontend-dashboard)
16. [Config & Hyperparameters](#16-config--hyperparameters)
17. [Test Suite](#17-test-suite)
18. [Key Design Decisions & Trade-offs](#18-key-design-decisions--trade-offs)

---

## 1. What the Project Does

Given a software project's characteristics (size, risk, domain, team, legacy debt, etc.), the system recommends which type of delivery team minimises Total Cost of Ownership:

| Label | Meaning |
|-------|---------|
| **Human** | Fully human engineering team — warranted for high risk, regulatory, or complex legacy work |
| **Hybrid** | Human oversight + AI assistance — the default for medium-complexity projects |
| **AI** | Mostly AI-driven delivery — feasible for low-risk, low-complexity, modern-stack projects |

It also predicts the **profit margin percentage** for that project using a regression model.

This is a **supervised ML classification + regression problem** trained on 1,600 synthetically generated project records (800 Greenfield + 800 Legacy).

---

## 2. GitHub Version History

There are **3 commits** on `main`. No tags exist yet. All three are on the same branch.

```
7f4fb9e  feat(frontend): rebuild dashboard with cost-model-specific UI   ← HEAD
a0dfdc7  feat: HybridEngine dark-mode observability dashboard (frontend v1)
28ea5c3  feat: v1.0 — TCO ensemble model with Greenfield + Legacy support
```

### Commit `28ea5c3` — v1.0 ML Model
The foundational commit. Contains everything ML-related:
- All `src/` Python modules (config, data synthesis, feature engineering, model, utils)
- Trained model artefacts in `models/`
- Full test suite (38 tests)
- 4-tab Streamlit dashboard (`app/dashboard.py`)
- SRS doc, methodology docs, notebooks, results

### Commit `a0dfdc7` — Wrong Frontend (HybridEngine)
Added a React + Tailwind frontend copied from a different project called "HybridEngine" — an agent orchestration observability platform. **The content was wrong for this project** (showed agent harness pipelines, comprehension debt, etc. instead of TCO model concepts). The aesthetic (dark tactical UI) was correct.

### Commit `7f4fb9e` — Correct Frontend (current HEAD)
Rebuilt the frontend with cost-model-specific content using the same dark aesthetic. This is the live version.

> **Both the wrong and correct frontend exist in git history** — `a0dfdc7` is the "wrong v1 frontend" and `7f4fb9e` is the corrected one. To see the wrong version: `git show a0dfdc7:app/frontend/index.html`.

---

## 3. Repository Layout

```
cost-optimization-model/
├── src/                          Core ML library
│   ├── config.py                 All constants, paths, feature schema, hyperparameters
│   ├── data_synthesis.py         Synthetic data generator (Greenfield + Legacy)
│   ├── feature_engineering.py    ColumnTransformer pipeline + train/val/test split
│   ├── model.py                  Stacking ensemble build, train, evaluate, infer
│   └── utils.py                  Logging, metrics, save helpers
│
├── app/
│   ├── dashboard.py              4-tab Streamlit app (interactive inference UI)
│   └── frontend/
│       └── index.html            React + Tailwind single-page dashboard (served via http.server)
│
├── models/
│   ├── xgboost_classifier.pkl    Trained classification pipeline (sklearn Pipeline)
│   ├── random_forest_classifier.pkl  Trained regression pipeline (misleading name — actually StackingRegressor)
│   └── model_metadata.json       All metrics, hyperparams, feature importances
│
├── data/
│   ├── processed/
│   │   ├── combined_features.csv         1600-row unified training dataset
│   │   └── greenfield_features.csv       800-row Greenfield subset
│   └── synthetic/
│       └── synthesis_log.json            Label distribution and margin stats from last synthesis run
│
├── results/
│   ├── metrics/sprint_one_evaluation.json  Val + test split metrics for both tasks
│   └── visualizations/
│       ├── confusion_matrix.png
│       └── feature_importance.png
│
├── tests/
│   ├── test_data_validation.py      Dataset integrity tests
│   ├── test_feature_engineering.py  Preprocessor shape and encoding tests
│   └── test_model.py               End-to-end inference tests including NFR-06
│
├── notebooks/
│   ├── 01_data_synthesis.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_feature_engineering.ipynb
│   └── 04_model_training.ipynb
│
└── docs/
    ├── SRS_IEEE_TCO_Model.docx
    ├── model_architecture.md
    ├── feature_rationale.md
    ├── data_generation_methodology.md
    └── REVERSE_ENGINEERING.md     ← this file
```

---

## 4. The Problem Being Solved

Software delivery has three team archetypes with very different cost profiles:

- **Human teams** are expensive but handle ambiguity, regulation, and novel complexity
- **AI tools** are cheap but brittle on complex, undocumented, high-risk work
- **Hybrid** is the pragmatic middle ground for most real projects

The model learns when to use which by training on synthetic projects where the "correct" label was assigned by hierarchical business rules derived from TCO research. The synthetic approach (vs. real data) gives full control over label distribution and rule transparency.

---

## 5. Data Synthesis

**File:** `src/data_synthesis.py`

### Why Synthetic Data?

Real project data is confidential, inconsistently recorded, and rarely labelled with team-type outcomes. Synthesis lets us:
1. Control the label distribution
2. Encode domain expertise as explicit rules
3. Reproduce the dataset exactly with a seed

### Two Populations

```
synthesise_greenfield(n=800, seed=42)   → project_type = 0
synthesise_legacy(n=800, seed=43)       → project_type = 1
synthesise_combined()                   → concat + shuffle → 1600 rows
```

### How Greenfield Records Are Made

1. **Sample categorical features** from weighted distributions:
   - `complexity_score`: [Low 30%, Medium 40%, High 30%]
   - `technical_risk_level`: [Low 25%, Med 35%, High 30%, Critical 10%]
   - `security_criticality`: same distribution as risk
   - etc.

2. **Derive numeric features** from complexity/risk indices:
   - `estimated_loc` ~ LogNormal(log([2K, 12K, 50K][complexity_idx]), 0.5) clipped to [500, 200K]
   - `timeline_days` ~ Normal(30 + 60×complexity_idx, 20) clipped to [7, 365]
   - `team_size_required` ~ Normal(2 + 3×complexity_idx, 1.5) clipped to [1, 20]
   - `integration_count` ~ Poisson(2 + 2×risk_idx) clipped to [0, 20]
   - `testing_coverage_pct` ~ Normal(55 + 10×complexity_idx, 15) clipped to [20, 98]

3. **Regulatory compliance** probability = base 15% + 30% if (Security/Data domain) + 20% if High/Critical risk

4. **Assign labels** via `_greenfield_rule()` (deterministic hierarchy) then add 5% noise (adjacent label flip)

5. **Fill legacy columns** with Greenfield defaults so the unified schema works

### How Legacy Records Differ

Legacy projects have **heavier distributions** — they're harder by nature:
- `complexity`: [Low 15%, Medium 40%, High 45%] vs Greenfield's [30%, 40%, 30%]
- `technical_risk_level`: [Low 15%, Med 30%, High 40%, Critical 15%] — more critical projects
- LOC range: [5K, 500K] vs [500, 200K] — legacy codebases are larger
- `budget_pressure`: Tight more common (40%) vs Greenfield (30%)

Plus **10 legacy-specific features** that don't exist for Greenfield projects:
- `technical_debt_score`, `documentation_quality`, `language_modernity`, `team_familiarity`
- `codebase_age_years`, `existing_test_coverage_pct`, `dependency_count`
- `last_refactor_years`, `incident_rate_monthly`, `code_duplication_pct`

Legacy features are **correlated** with each other realistically:
```python
age_base = 3 + 4 * debt_idx + 2 * (3 - lang_idx)  # older code = more debt, worse language
dep_count ~ LogNormal(log(50 + 30 * debt_idx), 0.6)  # more debt = more deps
incident_rate ~ Exponential(1 + 2 * debt_idx + risk_idx)  # debt + risk → incidents
```

---

## 6. Feature Schema

**File:** `src/config.py` → `ALL_FEATURES` (29 total)

### Shared Features (both Greenfield and Legacy)

| # | Feature | Type | Values |
|---|---------|------|--------|
| 1 | `project_type` | Binary | 0=Greenfield, 1=Legacy |
| 2 | `estimated_loc` | Numeric | Lines of code, [500, 500K] |
| 3 | `timeline_days` | Numeric | Project duration in days |
| 4 | `team_size_required` | Numeric | Headcount needed |
| 5 | `integration_count` | Numeric | External system integrations |
| 6 | `testing_coverage_pct` | Numeric | Required test coverage % |
| 7 | `complexity_score` | Ordinal | Low → Medium → High |
| 8 | `technical_risk_level` | Ordinal | Low → Medium → High → Critical |
| 9 | `seniority_required` | Ordinal | Junior → Mid → Senior → Architect |
| 10 | `documentation_level` | Ordinal | Minimal → Standard → Comprehensive |
| 11 | `performance_tier` | Ordinal | Standard → High → Real-time |
| 12 | `security_criticality` | Ordinal | Low → Medium → High → Critical |
| 13 | `budget_pressure` | Ordinal | Flexible → Moderate → Tight |
| 14 | `maintainability_req` | Ordinal | Low → Medium → High |
| 15 | `regulatory_compliance` | Binary | 0=No, 1=Yes |
| 16 | `domain_category` | Nominal | Web, Infrastructure, Security, Data, Mobile |

### Legacy-Specific Features (Greenfield rows filled with domain-sensible defaults)

| # | Feature | Type | Values | Greenfield Default |
|---|---------|------|--------|-------------------|
| 17 | `codebase_age_years` | Numeric | 1–30 years | 0 |
| 18 | `existing_test_coverage_pct` | Numeric | 0–85% | 0.0 |
| 19 | `dependency_count` | Numeric | 10–500 | 0 |
| 20 | `last_refactor_years` | Numeric | 0–15 years ago | 0 |
| 21 | `incident_rate_monthly` | Numeric | incidents/month | 0.0 |
| 22 | `code_duplication_pct` | Numeric | % duplicate code | 0.0 |
| 23 | `technical_debt_score` | Ordinal | Low → Medium → High → Critical | "Low" |
| 24 | `documentation_quality` | Ordinal | Poor → Minimal → Standard → Good | "Poor" |
| 25 | `language_modernity` | Ordinal | Legacy → Dated → Modern → Current | "Current" |
| 26 | `team_familiarity` | Ordinal | Unfamiliar → Low → Medium → High | "High" |

> **Why Greenfield gets "High" familiarity and "Current" language?** Because a Greenfield team built from scratch presumably knows the codebase they just created and is using current tooling. These defaults teach the model that `project_type=0` + `team_familiarity=High` is the Greenfield context.

---

## 7. Label Assignment Rules

### Greenfield Rules (`_greenfield_rule`)

The rules are a strict priority hierarchy — first match wins:

**→ HUMAN (override cases)**
1. `regulatory_compliance=1` AND `technical_risk_level` ∈ {High, Critical}
2. `security_criticality = Critical`
3. `security_criticality = High` AND `risk` ∈ {High, Critical}
4. `technical_risk_level = Critical`
5. `complexity = High` AND `seniority = Architect`
6. `performance_tier = Real-time` AND `risk = Critical`
7. `estimated_loc > 60,000` AND `complexity = High`

**→ AI (feasibility cases)**
1. `complexity=Low` AND `risk` ∈ {Low,Med} AND `security` ∈ {Low,Med} AND no regulation AND `loc < 10K`
2. `budget=Tight` AND `complexity=Low` AND `risk=Low`
3. `complexity=Low` AND `seniority` ∈ {Junior,Mid} AND `risk=Low` AND no regulation

**→ HYBRID** (default — everything else)

### Legacy Rules (`_legacy_rule`)

Inherits all Greenfield rules, then adds:

**→ HUMAN (legacy-specific)**
- `technical_debt_score = Critical`
- `debt = High` AND `team_familiarity` ∈ {Unfamiliar, Low} → comprehension debt risk
- `language_modernity = Legacy` AND `complexity` ∈ {Medium, High} → AI tooling can't help with old stacks
- `doc_quality = Poor` AND `familiarity` ∈ {Unfamiliar, Low} AND `complexity = High` → knowledge gap
- `codebase_age > 15` AND `debt` ∈ {High, Critical}
- `incident_rate > 10` AND `risk` ∈ {High, Critical}
- `code_duplication > 40%` AND `complexity = High`
- `loc > 150K` AND `debt` ∈ {High, Critical}

**→ AI (legacy-specific relaxed conditions)**
- `complexity=Low` AND `debt` ∈ {Low,Med} AND `language` ∈ {Modern,Current} AND `familiarity` ∈ {Medium,High} AND `risk` ∈ {Low,Med} AND no regulation

### 5% Noise Injection

After rule-based labelling, 5% of records are flipped to an adjacent class:
```python
adjacent = {"Human": "Hybrid", "Hybrid": random.choice(["Human","AI"]), "AI": "Hybrid"}
```
This prevents the model from perfectly memorising the rules and forces it to learn robustly.

---

## 8. NFR-06 Safety Gate

NFR-06 is a **non-functional requirement** (business constraint) that overrides ML predictions:

> **Critical-risk or Critical-security projects must NEVER be routed to an AI team.**

It appears in:
- The label assignment rules (enforced during data synthesis, so the model learns it)
- The rule-based JS simulator in the frontend (displayed as a badge)
- Test suite (`test_legacy_critical_debt_recommends_human`, etc.)

The gate fires when: `technical_risk_level = Critical` OR `security_criticality = Critical`

This is a hard constraint, not a soft preference. The model achieves this by learning from training data where this rule was always applied — there are zero `AI`-labelled records with Critical risk in the training set.

---

## 9. Profit Margin Formula

The regression target `profit_margin_pct` is calculated from features, not a real financial model. It approximates TCO economics:

```
margin = 100
       - labour_cost    (30 + 20×seniority + 10×team_norm + 5×loc_norm)
       - risk_cost      (5×risk + 5×security + 3×reg + 2×integrations)
       - overhead       (4×doc + 3×test_cov + 3×perf + 2×maintainability)
       - complexity     (10×complexity)
       + budget_benefit (5×budget_pressure)
       + noise(0, 1.5)
```

**Legacy adds extra cost terms:**
```
       - debt_cost         (8 × debt_score)        technical debt servicing
       - incident_cost     (6 × incident_rate/20)   incident remediation
       - familiarity_cost  (4 × (1 - familiarity))  knowledge transfer
       - lang_cost         (3 × (1 - lang_modernity)) old-stack tooling premium
       - doc_quality_cost  (2 × (1 - doc_quality))  documentation gap
       - dup_cost          (2 × duplication/60)     duplication rework
```

Result is clipped to [0, 75] for Greenfield and [2, 70] for Legacy.

---

## 10. Feature Engineering Pipeline

**File:** `src/feature_engineering.py`

The preprocessor is a `sklearn.compose.ColumnTransformer` with 7 transformers:

| Transformer | Columns | Transform | Why |
|-------------|---------|-----------|-----|
| `proj_type` | `project_type` | PassThrough | Already 0/1 binary |
| `num` | 5 numeric features | `StandardScaler` | Normalise scale for ANN/LR |
| `ord` | 8 ordinal features | `OrdinalEncoder` | Rank-preserving integer encoding |
| `bin` | `regulatory_compliance` | PassThrough | Already 0/1 |
| `nom` | `domain_category` | `OneHotEncoder(drop='first')` | 5 categories → 4 dummies |
| `leg_num` | 6 legacy numeric | `StandardScaler` | Greenfield rows all zeros — model learns 0=GF |
| `leg_ord` | 4 legacy ordinal | `OrdinalEncoder` | Same as shared ordinals |

### Train/Val/Test Split

```
Total: 1600 records
├── Test:  15%  = 240 records  (held out entirely)
├── Val:   15%  = 240 records  (used for early stopping / monitoring)
└── Train: 70%  = 1120 records

Stratified by target_team_label to maintain class balance across splits.
Val fraction = 0.15 / (1 - 0.15) = 0.1765 of the train+val set.
```

### OrdinalEncoder Logic

Ordinals are encoded in their natural rank order:
- `complexity_score`: Low=0, Medium=1, High=2
- `technical_risk_level`: Low=0, Medium=1, High=2, Critical=3
- Unknown values get `-1` (handle_unknown="use_encoded_value")

This preserves ordinality — the model can learn "higher risk = higher cost" monotonically.

### Why Not OneHotEncode All Categoricals?

OneHotEncoding ordinals would destroy the ordering information. If `High=2` is represented as `[0,0,1]` the model can't infer it's "more than" `Medium=1`. OrdinalEncoder keeps the rank as a single integer.

---

## 11. Model Architecture

**File:** `src/model.py`

### Classification Pipeline

```
Input DataFrame (29 features)
        ↓
ColumnTransformer (preprocessor)
        ↓
StackingClassifier
    ├── XGBoost Classifier     (n=300, depth=5, lr=0.05)
    ├── Decision Tree          (depth=6, class_weight='balanced')
    ├── ANN / MLPClassifier    (128→64→32, ReLU, Adam, early_stopping)
    └── Logistic Regression    (C=1.0, linear baseline)
            ↓ (5-fold cross-val out-of-fold predictions + passthrough=True)
    Meta-Learner: Logistic Regression
        ↓
    Predicted class: Human / Hybrid / AI
    + Probabilities for each class
```

### Regression Pipeline

```
Input → ColumnTransformer → StackingRegressor
    ├── XGBoost Regressor
    ├── Decision Tree Regressor
    ├── ANN / MLPRegressor     (same 128→64→32 arch)
    └── Linear Regression
            ↓ (5-fold CV + passthrough=True)
    Meta-Learner: Ridge Regression (alpha=1.0)
        ↓
    Predicted profit_margin_pct
```

### What Is Stacking?

Stacking (aka stacked generalisation) trains base learners on the full training set using k-fold cross-validation to produce **out-of-fold predictions**. These OOF predictions become the meta-learner's training features. At inference:
1. All base learners predict on the new input
2. Their predictions are concatenated into a meta-feature vector
3. The meta-learner makes the final prediction

`passthrough=True` means the meta-learner also receives the **original preprocessed features** alongside the base-learner predictions — giving it full context.

### Why XGBoost + DT + ANN + LR?

Each learner captures different structure:
- **XGBoost** — gradient boosted trees, handles non-linearities, interactions, mixed types well
- **Decision Tree** — interprets the explicit rule-based structure in the training data directly
- **ANN** — captures smooth non-linear boundaries, good with normalised numerics
- **Logistic Regression** — linear baseline; prevents ensemble from over-fitting noise, acts as regulariser

If one learner dominates, the others add diversity and prevent overconfidence.

### Why Logistic Regression as Meta-Learner (not XGBoost)?

A simple meta-learner is intentional:
- Prevents the stacking ensemble from re-memorising the training data
- Forces the meta-learner to find a reliable weighted combination of base outputs
- Logistic Regression is inherently calibrated (outputs are proper probabilities)

---

## 12. Training & Evaluation

### Training Sequence (`run_training`)

```python
1. train_classifier(X_train, y_clf_train)     # fits clf pipeline
2. train_regressor(X_train, y_rgr_train)      # fits rgr pipeline
3. evaluate_classifier(X_val, ...)            # val metrics
4. evaluate_classifier(X_test, ...)           # test metrics (reported)
5. evaluate_regressor(X_val, ...)             # val MAPE/R²
6. evaluate_regressor(X_test, ...)            # test MAPE/R² (reported)
7. evaluate_base_learners(...)                # individual base learner scores
8. extract_feature_importance()              # XGBoost feature importances
9. plot_confusion_matrix()                   # saved to results/
10. plot_feature_importance()               # saved to results/
11. save_artefacts()                         # .pkl + model_metadata.json
```

### Classification Metrics Computed

- Accuracy, Precision (weighted), Recall (weighted), F1 (weighted)
- Per-class: Precision, Recall, F1, Support
- Confusion Matrix (3×3: Human/Hybrid/AI)

### Regression Metrics Computed

- **MAPE** (Mean Absolute Percentage Error) — primary metric, target < 5.5%
- **RMSE** (Root Mean Squared Error)
- **MAE** (Mean Absolute Error)
- **R²** (coefficient of determination)

---

## 13. Model Performance

All figures from `models/model_metadata.json` (test split, 240 records):

### Classification

| Metric | Value | NFR Target |
|--------|-------|------------|
| Accuracy | **90.0%** | ≥ 85% ✓ |
| Precision (weighted) | 89.96% | — |
| Recall (weighted) | 90.0% | — |
| F1 (weighted) | 89.69% | — |

**Per-Class Breakdown:**

| Class | Precision | Recall | F1 | Support |
|-------|-----------|--------|-----|---------|
| Human | 88.9% | 53.3% | 66.7% | 15 |
| Hybrid | 93.1% | 95.7% | 94.4% | 141 |
| AI | 84.9% | 86.9% | 85.9% | 84 |

> Human has low recall (53.3%) because it's the minority class (15 test samples) and the rules overlap with Hybrid for borderline cases. The 5% noise during synthesis also means some true-Human cases were labelled Hybrid in the training data.

**Confusion Matrix (rows=actual, cols=predicted):**
```
           Human  Hybrid  AI
Human  [    8,     0,    7 ]
Hybrid [    0,   135,    6 ]
AI     [    1,    10,   73 ]
```

**Base Learner Comparison:**

| Model | Accuracy |
|-------|----------|
| XGBoost | 93.36% |
| Decision Tree | 84.23% |
| ANN | 85.06% |
| Logistic Regression | 82.16% |
| **Ensemble (stacked)** | **90.00%** |

> XGBoost alone outperforms the stacked ensemble on accuracy. The stacking adds calibration and robustness at the cost of 3 points of raw accuracy.

### Regression

| Metric | Value | NFR Target |
|--------|-------|------------|
| **MAPE** | **5.37%** | ≤ 5.5% ✓ |
| R² | 0.986 | — |
| RMSE | ~1.2% | — |

---

## 14. Inference Flow

**File:** `src/model.py` → `predict()`

```python
result = predict(clf_pipe, rgr_pipe, X_new)
# Returns:
{
    "recommended_team": "Hybrid",
    "probabilities": {"Human": 0.05, "Hybrid": 0.87, "AI": 0.08},
    "predicted_profit_margin_pct": 42.3
}
```

**Step-by-step:**
1. `clf_pipe.predict(X)` → integer class index (0=Human, 1=Hybrid, 2=AI)
2. `label_encoder.inverse_transform([idx])` → string label
3. `clf_pipe.predict_proba(X)` → [p_Human, p_Hybrid, p_AI]
4. `rgr_pipe.predict(X)` → predicted profit margin

For the **frontend** (no Python backend), a JavaScript rule-based simulator re-implements the same hierarchical decision rules to approximate the ML model's behaviour directly in the browser.

---

## 15. Frontend Dashboard

**File:** `app/frontend/index.html`

A single-file React + Tailwind CSS dashboard. No build step — Babel standalone compiles JSX in-browser. Served via `python3 -m http.server 8502`.

### Why Single Inline Script?

`<script type="text/babel" src="file.jsx">` loads **asynchronously** and each script runs in its own isolated Babel scope. Functions don't hoist to `window` in strict mode. Solution: all JSX is inlined in one `<script type="text/babel">` block so all component functions share a single scope.

### Four Dashboard Sections

**Section 1 — Model KPIs** (`ModelKPIs`)
Four cards with real metrics from `model_metadata.json`:
- Accuracy: 90.0% (with sparkline)
- MAPE: 5.37% (regression error)
- R²: 0.986 (regression fit)
- Training Records: 1,600

**Section 2 — Prediction Engine** (`PredictionEngine`)
Three side-by-side panels:
1. **ProjectForm** — 29-feature input form with Greenfield/Legacy toggle. Legacy shows 10 extra fields. On submit, calls `simulatePredict()`.
2. **EnsemblePipeline** — 4-step visual flow: Data Preprocessing → Base Learners (XGB+DT+ANN+LR) → Meta-Learner (LR/Ridge) → Recommendation Output
3. **PredictionOutput** — Team badge (colour-coded), probability bars for all 3 classes, margin gauge, NFR-06 gate indicator if triggered, feature signal pills

**Section 3 — Analytics Row**
- `FeatureImportance` — horizontal bar chart of top 13 features (from `model_metadata.json`)
- `PerClassMetrics` — precision/recall/F1 bars per class
- `LabelDistribution` — stacked bars showing Greenfield vs Legacy label counts

**Section 4 — Team Economics** (`TeamEconomics`)
- Human / Hybrid / AI cost comparison cards
- Editable rate assumptions ($/hr, team sizes, AI tool cost)
- Live compute ticker (simulates cost accumulating over time)
- Delta strip showing savings vs. human baseline

### Rule-Based JS Simulator (`simulatePredict`)

Implements the same priority hierarchy as `_greenfield_rule` and `_legacy_rule`:

```javascript
function simulatePredict(f) {
    // NFR-06 gate
    if (risk >= 3 || sec >= 3)
        return { team: 'Human', gate: 'NFR-06', ... }

    if (isLegacy) {
        if (debt === 'Critical') return Human
        if (debt === 'High' && familiarity in ['Unfamiliar','Low']) return Human
        if (lang === 'Legacy' && complexity in ['Medium','High']) return Human
        // ... all legacy rules
        if (lowDebt && modernStack && familiar && lowRisk) return AI
    } else {
        // Greenfield rules
        if (regulatory && highRisk) return Human
        if (lowComp && lowRisk && lowSec && smallLOC) return AI
    }
    return Hybrid
}
```

### Dark Tactical Aesthetic

| Token | Value | Usage |
|-------|-------|-------|
| `--ink-900` | `#0B0F19` | Main background |
| `--ink-800` | `#111827` | Card backgrounds |
| `--ink-700` | `#1F2937` | Borders |
| `--emerald2` | `#34D399` | Success / AI label |
| `--amber2` | `#FBBF24` | Warning / Hybrid label |
| `--crimson2` | `#F87171` | Error / Human label |
| `--azure` | `#60A5FA` | Accent / links |
| Font (metrics) | JetBrains Mono | Tabular numbers |
| Font (copy) | Inter | UI text |

---

## 16. Config & Hyperparameters

**File:** `src/config.py`

### XGBoost Classifier

```python
n_estimators=300, max_depth=5, learning_rate=0.05,
subsample=0.8, colsample_bytree=0.8,
min_child_weight=3, gamma=0.1,
reg_alpha=0.1, reg_lambda=1.0
```
- Low learning rate (0.05) + many trees (300) → gradual, stable learning
- Subsampling (0.8) → reduces overfitting via row/column sampling
- `gamma=0.1` → minimum loss reduction required for a split (conservative)

### ANN (MLPClassifier)

```python
hidden_layer_sizes=(128, 64, 32),  # 3-layer pyramid
activation='relu', solver='adam',
alpha=0.001,                        # L2 regularisation
max_iter=500, early_stopping=True,
n_iter_no_change=20                 # patience
```
- Pyramid architecture (128→64→32) gradually compresses features
- Early stopping prevents overfit on the ANN

### Decision Tree

```python
max_depth=6, min_samples_split=8, min_samples_leaf=4,
class_weight='balanced'
```
- `class_weight='balanced'` compensates for class imbalance (Human is rare)
- Depth 6 is enough to capture the rule hierarchy without overfit

### Meta-Learner

- **Classifier meta**: `LogisticRegression(C=1.0)` — moderate regularisation
- **Regressor meta**: `Ridge(alpha=1.0)` — L2 regularised linear

### Reproducibility

`SEED = 42` is passed to every stochastic component. Combined with fixed data synthesis seeds, the entire pipeline is 100% reproducible (NFR-07).

---

## 17. Test Suite

**38 tests across 3 files**, all passing.

### `test_data_validation.py`
- Dataset loads and has correct shape (1600 rows × 31 columns)
- No nulls in required columns
- Label distribution within expected ranges per project type
- Margin values within [0, 75]
- Both project types present

### `test_feature_engineering.py`
- Preprocessor outputs correct number of columns
- Ordinal encoding preserves ordering (Critical > High > Medium > Low)
- OneHotEncoder produces correct domain dummies
- Train/val/test split sizes are correct
- Stratification maintains class distribution

### `test_model.py`
- Greenfield inference: low-risk simple project → AI
- Greenfield inference: high-risk regulated → Human
- Legacy inference: critical debt + unfamiliar team → Human
- Legacy inference: modern stack, low debt, familiar → AI
- NFR-06: Critical risk project never routes to AI regardless of other features
- NFR-06: Critical security project never routes to AI
- Probability outputs sum to 1.0
- Margin prediction within [2, 75]
- All 3 class labels are reachable

---

## 18. Key Design Decisions & Trade-offs

### 1. Synthetic Data Over Real Data

**Decision:** Generate 1,600 synthetic records instead of gathering real project data.

**Why:** Real project data is unavailable (confidential), inconsistently formatted, and lacks ground-truth team-type labels.

**Trade-off:** The model learns the synthesis rules, not real-world project economics. Predictions are only as good as the rules that generated the training data.

### 2. Stacking Over Single Model

**Decision:** Use 4-base-learner stacking instead of just XGBoost (which achieves higher raw accuracy).

**Why:** Stacking adds calibration (reliable probabilities), handles edge cases differently across learners, and is more robust to distribution shift.

**Trade-off:** XGBoost alone gets 93.36% accuracy vs ensemble's 90.0%. The ensemble trades 3.4 points of accuracy for better-calibrated probabilities and robustness.

### 3. Greenfield Defaults for Legacy Columns

**Decision:** Fill Greenfield records' legacy columns with sensible defaults (age=0, debt="Low", etc.) rather than imputing NaN at inference time.

**Why:** Avoids the imputer needing to handle cross-type missingness. The model learns `project_type=0 + age=0 + debt=Low` = Greenfield context.

**Trade-off:** The model sees artificial values for Greenfield rows. If a future Greenfield project somehow has a non-zero `codebase_age`, the model might misinterpret it.

### 4. Rule-Based JS Simulator (No Backend)

**Decision:** The frontend runs a hand-coded JS rule simulator instead of calling a Python inference API.

**Why:** Eliminates the need for a Flask/FastAPI server, making the app deployable as a static file served by any HTTP server.

**Trade-off:** The JS simulator approximates the ML model — it implements the same rules but can't replicate the learned weights from the meta-learner. Probability scores are heuristic, not the model's actual `.predict_proba()` output.

### 5. PassThrough=True in Stacking

**Decision:** The meta-learner sees both base-learner outputs AND the original preprocessed features.

**Why:** Gives the meta-learner more context. It can learn "XGBoost says Hybrid AND the raw risk score is Low → probably AI, not Hybrid."

**Trade-off:** More input dimensions for the meta-learner; slightly higher risk of overfitting at the meta level (mitigated by using a regularised LR meta-learner).

---

*Generated: 2026-05-22 | Model version: 1.0.0 | Commits: 28ea5c3 (ML), a0dfdc7 (frontend v1), 7f4fb9e (frontend corrected)*
