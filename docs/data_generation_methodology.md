# Data Generation Methodology

## Overview

Sprint One uses a synthesised dataset of 800 greenfield project records. Real-world SRS datasets are not publicly available at the scale required for supervised ML training, so domain-informed synthesis is the standard approach for this class of problem.

## Why Synthesis?

1. **No public SRS dataset exists** at the required granularity (project-level structured attributes with TCO outcomes).
2. **Real data has privacy constraints** — client project data from IT service firms is commercially sensitive.
3. **Controlled synthesis enables reproducibility** — the generation process is fully documented, seeded, and re-runnable.
4. **Domain validity is preserved** — all feature distributions and label assignment rules are grounded in the empirical findings of Dharne (2026) and McKinsey AI Economics (2026).

## Feature Distributions

Each feature is sampled from a realistic probability distribution:

| Feature | Distribution | Rationale |
|---|---|---|
| `estimated_loc` | Log-normal around complexity-conditioned base | LOC distributions in real projects are log-normally distributed |
| `timeline_days` | Normal(μ=30+60×complexity_idx, σ=20) clipped to [7, 365] | Longer for complex projects |
| `team_size_required` | Normal(μ=2+3×complexity_idx, σ=1.5) clipped to [1, 20] | Scales with complexity |
| `integration_count` | Poisson(λ=2+2×risk_idx) | Integration count is count-distributed |
| `testing_coverage_pct` | Normal(μ=55+10×complexity_idx, σ=15) | Higher coverage expected on complex projects |
| All ordinal features | Categorical with domain-informed probabilities | Matching real-world project type frequencies |
| `regulatory_compliance` | Bernoulli with domain-adjusted probability | Higher in Security/Data domains |

## Label Assignment Logic

Labels are assigned by a **hierarchical business-rule function** designed to match the TCO research findings:

### Human (highest priority)
Projects with any of the following characteristics:
- Regulatory compliance required AND risk level High/Critical
- Security criticality = Critical
- Security = High AND risk = High/Critical
- Technical risk = Critical
- Complexity = High AND seniority = Architect
- Performance = Real-time AND risk = Critical
- LOC > 60,000 AND complexity = High

**Rationale**: These characteristics trigger the Productivity-Reliability Paradox identified in Dharne (2026). The PocketOS case study showed that autonomous AI agents in critical-risk scenarios can cause catastrophic failures (entire production database deleted in 9 seconds). Human oversight is the only acceptable configuration.

### AI (second priority — only if Human conditions not met)
Projects with all of the following:
- Complexity = Low AND risk ∈ {Low, Medium} AND security ∈ {Low, Medium} AND not regulated AND LOC < 10,000
- OR: Budget = Tight AND complexity = Low AND risk = Low
- OR: Complexity = Low AND seniority ∈ {Junior, Mid} AND risk = Low AND not regulated

**Rationale**: Small, low-risk, non-regulated projects are where AI marginal cost (~INR 100/1,000 LOC) creates genuine economic advantage over human developers (~INR 13,000/month). Comprehension debt accumulation is negligible at this scale.

### Hybrid (default)
All remaining projects — medium complexity, moderate risk, or projects with mixed signals.

### Label Noise
A 5% random flip to the adjacent class is applied to simulate real-world human judgement variability near decision boundaries.

## Profit Margin Formula

The profit margin is computed **directly from features** (not from the team label) to enable clean ML regression:

```
margin = 100% - labour_cost - risk_cost - overhead_cost - complexity_cost + budget_benefit
```

Component breakdown:
- **Labour cost** (30–65%): driven by seniority, team size, LOC, timeline
- **Risk cost** (0–20%): driven by technical risk, security, regulatory compliance, integrations
- **Overhead** (0–15%): driven by documentation level, testing coverage, performance tier, maintainability
- **Complexity penalty** (0–10%): driven by complexity score
- **Budget benefit** (0–5%): tight budget pressure forces efficiency

A small Gaussian noise (σ=1.5%) is added to each record to simulate real-world variance.

## Validation

The generated dataset was validated against:
1. Programmatic schema validation (`validate_dataframe()`)
2. Class balance inspection (target: ~42% Hybrid, ~38% Human, ~11% AI + noise)
3. Profit margin range plausibility (0–75%)
4. Feature correlation checks (no spurious perfect correlations)

## Reproducibility

All synthesis runs are seeded with `SEED=42`. The synthesis log is written to `data/synthetic/synthesis_log.json` on every run.
