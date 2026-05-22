# TCO Optimisation Model

**Team Composition Decision Support for Software Development Projects**

> Sprint One: Greenfield Projects | University of Essex · Soham Nageshkumar Dharne · 2026

---

## What This Is

A supervised machine learning system that predicts the optimal team composition — **Human**, **AI Agent**, or **Hybrid** — for a software development project, along with the expected profit margin under that configuration.

It addresses a real gap in industry practice: organisations compare staffing costs naively (hourly rate vs. API fees) without accounting for the full TCO — hallucination-induced rework, comprehension debt, production failure costs, and regulatory liability. This model quantifies those hidden costs and makes the decision rigorous.

Grounded in: *Socio-Cognitive Dynamics of Pure Automation vs. Hybrid Orchestration in Software Engineering* (Dharne, University of Essex, 2026).

---

## Results (Sprint One)

| Metric | Target | Achieved |
|---|---|---|
| Classification accuracy | >= 85% | **93.3%** |
| Profit margin MAPE | <= 5% | **3.48%** |
| Regression R2 | — | **0.972** |
| Recall (Human/safety) | Maximise | **93.3%** |
| NFR-06 (no AI on critical) | 100% | **100%** |
| All unit tests | 28 pass | **28/28** |

---

## Ensemble Architecture

```
                    ┌─────────────────────────────────┐
Input (15 features) │       ColumnTransformer          │
                    │  StandardScaler | OrdinalEncoder │
                    │  OneHotEncoder  | PassThrough     │
                    └──────────────┬──────────────────┘
                                   │ 18 features
                    ┌──────────────▼──────────────────┐
                    │       Stacking Ensemble           │
                    │  ┌──────────┐ ┌───────────────┐  │
                    │  │ XGBoost  │ │ Decision Tree │  │
                    │  └──────────┘ └───────────────┘  │
                    │  ┌──────────┐ ┌───────────────┐  │
                    │  │   ANN    │ │ Linear / LR   │  │
                    │  └──────────┘ └───────────────┘  │
                    │         Meta-learner              │
                    │    (Logistic / Ridge Regr.)       │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │  Human / Hybrid / AI + Margin %  │
                    └─────────────────────────────────┘
```

---

## Setup

```bash
# 1. Clone and install
git clone <repo-url>
cd cost-optimization-model
pip install -r requirements.txt

# 2. Generate synthetic dataset
cd src
python data_synthesis.py

# 3. Train ensemble models
python model.py

# 4. Run tests
cd ..
python -m pytest tests/ -v

# 5. Launch dashboard
streamlit run app/dashboard.py
```

---

## Project Structure

```
cost-optimization-model/
├── src/
│   ├── config.py               # Paths, feature schema, hyperparameters
│   ├── data_synthesis.py       # Synthetic SRS data generator
│   ├── feature_engineering.py  # sklearn preprocessing pipeline
│   ├── model.py                # Stacking ensemble (train, eval, infer)
│   └── utils.py                # Serialisation, validation, metrics
├── data/
│   └── processed/
│       └── greenfield_features.csv   # 800 synthetic SRS records
├── models/
│   ├── xgboost_classifier.pkl        # Trained classification pipeline
│   ├── random_forest_classifier.pkl  # Trained regression pipeline
│   └── model_metadata.json           # Metrics + feature importance
├── results/
│   ├── metrics/sprint_one_evaluation.json
│   └── visualizations/
│       ├── confusion_matrix.png
│       └── feature_importance.png
├── app/
│   └── dashboard.py            # Streamlit decision-support UI
├── notebooks/
│   ├── 01_data_synthesis.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_feature_engineering.ipynb
│   └── 04_model_training.ipynb
├── tests/                      # 28 unit tests (all passing)
└── docs/
    ├── data_generation_methodology.md
    ├── feature_rationale.md
    └── model_architecture.md
```

---

## Key Design Decisions

**Why stacking, not voting?**
The meta-learner learns when to trust each base learner. XGBoost dominates on ordinal feature signals; the ANN captures non-linear interactions between security and compliance features. Averaging would blend these at equal weight regardless of context.

**Why no deep learning?**
800 structured tabular records. Deep learning requires unstructured data at scale. XGBoost + sklearn MLP achieves higher accuracy with 100% reproducibility, no GPU dependency, and interpretable feature importances (hard requirement: FR-20).

**Why synthetic data?**
No public SRS dataset exists at this granularity. All synthesis logic is domain-informed, fully documented, and reproducible from `SEED=42`. See `docs/data_generation_methodology.md`.

**Why recall > precision?**
A false negative (recommending pure AI for a project needing human oversight) costs orders of magnitude more than a false positive. The PocketOS case study (Dharne, 2026) — autonomous AI agent deleted an entire production database in 9 seconds — quantifies this asymmetry.

---

## Reproducibility

All runs are seeded at `SEED=42` in `src/config.py`. Re-running `python src/data_synthesis.py && python src/model.py` from any machine produces identical results.

---

## References

1. Dharne, S.N. — *Socio-Cognitive Dynamics of Pure Automation vs. Hybrid Orchestration*, University of Essex, 2026
2. Ahmad, M.O. — *Comprehension Debt in GenAI-Assisted SE Projects*, EASE 2026
3. Brynjolfsson et al. — *Micro Gains, Macro Disappointment*, Stanford Digital Economy Lab, 2025
4. McKinsey Global AI Survey — *The Economics of Agentic Automation*, 2026
5. IEEE Std 830-1998 — *Recommended Practice for Software Requirements Specifications*
