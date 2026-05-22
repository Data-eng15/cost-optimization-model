# Feature Rationale

This document explains why each of the 17 features in the dataset was chosen and how it contributes to the TCO prediction task.

## Numeric Features

### `estimated_loc` — Estimated Lines of Code
**Why it matters**: LOC is a primary driver of comprehension debt (Ahmad, 2026). Large codebases accumulate knowledge that AI agents cannot reliably maintain across context windows. Projects over 40,000 LOC have disproportionately high hallucination-induced rework costs under pure AI configurations.

**Encoding**: Log-normalised internally; StandardScaler applied in preprocessing.

---

### `timeline_days` — Calendar Days Available
**Why it matters**: Tight timelines favour AI acceleration. Extended timelines signal complex projects requiring sustained human reasoning. Timeline also interacts with `team_size_required` to imply per-developer daily output targets.

**Encoding**: StandardScaler.

---

### `team_size_required` — Number of Developers Required
**Why it matters**: Large teams imply coordination overhead that AI agents cannot handle autonomously. Human team leads are required for communication and decision-making at scale.

**Encoding**: StandardScaler.

---

### `integration_count` — Number of External System Integrations
**Why it matters**: Each integration is a potential AI hallucination vector — AI agents frequently generate plausible but incorrect API call structures. Human developers catch these through contextual understanding of system contracts.

**Encoding**: StandardScaler.

---

### `testing_coverage_pct` — Expected Test Coverage Percentage
**Why it matters**: High test coverage requirements imply mature QA processes that benefit from human test design. AI-generated tests tend to test implementation rather than behaviour.

**Encoding**: StandardScaler.

---

## Ordinal Features

All ordinal features are encoded with `OrdinalEncoder` to preserve rank information. This is appropriate for both tree-based models (XGBoost, DT) and distance-sensitive models (ANN, Logistic Regression), as the ranking carries genuine semantic meaning.

### `complexity_score` — Low / Medium / High
**Why it matters**: The most discriminative single feature. High complexity correlates strongly with Human recommendation due to comprehension debt accumulation and architectural decision density.

---

### `technical_risk_level` — Low / Medium / High / Critical
**Why it matters**: Critical-risk projects (banking systems, infrastructure, safety-critical software) categorically require human oversight per NFR-06. Risk level also drives rework probability in the cost model.

---

### `seniority_required` — Junior / Mid / Senior / Architect
**Why it matters**: Architect-level requirements indicate the project has complex cross-cutting concerns (system design, technology selection, security architecture) that current AI agents cannot reliably handle.

---

### `documentation_level` — Minimal / Standard / Comprehensive
**Why it matters**: Comprehensive documentation requirements favour human teams. AI-generated documentation tends to be accurate for code-level details but poor for rationale, trade-off explanation, and architectural narrative.

---

### `performance_tier` — Standard / High / Real-time
**Why it matters**: Real-time systems (trading platforms, medical devices, industrial control) require performance reasoning at a depth that AI agents currently lack. Profiling, latency analysis, and hardware-aware optimisation remain human-dominated skills.

---

### `security_criticality` — Low / Medium / High / Critical
**Why it matters**: Security is the strongest single predictor of Human recommendation. Critical security projects (payment systems, authentication, cryptographic protocols) require adversarial thinking that AI agents are demonstrably poor at (see Dharne, 2026 pen-test case studies).

---

### `budget_pressure` — Flexible / Moderate / Tight
**Why it matters**: Tight budget pressure is the primary economic driver for AI adoption. When cost minimisation is paramount and risk is acceptable, AI marginal costs (INR 100/1,000 LOC) create compelling economic advantage.

---

### `maintainability_req` — Low / Medium / High
**Why it matters**: High maintainability requirements imply long-term codebase stewardship. AI-assisted codebases accumulate comprehension debt over time; human teams are better at sustainable architecture design.

---

## Binary Features

### `regulatory_compliance` — 0 or 1
**Why it matters**: A hard constraint. Regulated projects (GDPR, HIPAA, PCI-DSS, FSA) require human accountability chains that AI systems cannot provide. This is the highest-weight feature in the Human decision rule.

**Encoding**: PassThrough (already 0/1).

---

## Nominal Features

### `domain_category` — Web / Infrastructure / Security / Data / Mobile
**Why it matters**: Domain sets context-specific risk priors. Security-domain projects carry elevated human requirements. Data-domain projects may be more AI-amenable (structured ETL pipelines). Infrastructure projects carry high blast-radius risk.

**Encoding**: OneHotEncoder with `drop='first'` (Infrastructure as baseline category) to avoid multicollinearity in linear models.

---

## Target Variables

### `target_team_label` — Human / Hybrid / AI
The primary classification target. Assigned by hierarchical business rules derived from TCO research.

### `profit_margin_pct` — Float [0, 75]
The regression target. Computed from features via a cost model parameterised on labour, risk, overhead, and complexity components. Directly learnable from features without requiring knowledge of the team label.
