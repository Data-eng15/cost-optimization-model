"""
Synthetic SRS dataset generator — Greenfield + Legacy (Sprint One + Two).

Label assignment uses hierarchical business rules derived from TCO research
(Dharne, 2026). Legacy projects have additional signals: technical debt,
codebase age, documentation quality, team familiarity, and incident rate —
all of which shift the Human/AI tradeoff significantly versus greenfield.

The combined dataset is saved to data/processed/combined_features.csv.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from config import (
    CLASS_LABELS, DATA_PROCESSED, DATA_SYNTHETIC, DOMAIN_CATEGORIES,
    GREENFIELD_LEGACY_DEFAULTS, LEGACY_NUMERIC_FEATURES,
    LEGACY_ORDINAL_FEATURES, N_SAMPLES, ORDINAL_FEATURES,
    SEED, TARGET_CLASS, TARGET_REGR,
)

# ---------------------------------------------------------------------------
# Shared ordinal maps
# ---------------------------------------------------------------------------
_ALL_ORD = {
    **{col: {v: i for i, v in enumerate(lvls)} for col, lvls in ORDINAL_FEATURES.items()},
    **{col: {v: i for i, v in enumerate(lvls)} for col, lvls in LEGACY_ORDINAL_FEATURES.items()},
}


def _score(val: str, col: str) -> int:
    return _ALL_ORD[col].get(val, 0)


# ===========================================================================
# GREENFIELD
# ===========================================================================

def synthesise_greenfield(n: int = N_SAMPLES, seed: int = SEED) -> pd.DataFrame:
    """800 synthetic greenfield SRS records."""
    rng = np.random.default_rng(seed)
    rows = [_make_greenfield_record(rng) for _ in range(n)]
    df = pd.DataFrame(rows)
    df["project_type"] = 0   # 0 = Greenfield
    # Fill legacy columns with greenfield defaults
    for col, val in GREENFIELD_LEGACY_DEFAULTS.items():
        df[col] = val
    _assign_greenfield_labels(df, rng)
    _assign_greenfield_margin(df, rng)
    return df


def _make_greenfield_record(rng: np.random.Generator) -> dict:
    complexity   = rng.choice(["Low", "Medium", "High"], p=[0.30, 0.40, 0.30])
    risk         = rng.choice(["Low", "Medium", "High", "Critical"], p=[0.25, 0.35, 0.30, 0.10])
    security     = rng.choice(["Low", "Medium", "High", "Critical"], p=[0.25, 0.35, 0.30, 0.10])
    seniority    = rng.choice(["Junior", "Mid", "Senior", "Architect"], p=[0.20, 0.35, 0.35, 0.10])
    domain       = rng.choice(DOMAIN_CATEGORIES, p=[0.30, 0.20, 0.15, 0.25, 0.10])
    doc_level    = rng.choice(["Minimal", "Standard", "Comprehensive"], p=[0.25, 0.50, 0.25])
    perf_tier    = rng.choice(["Standard", "High", "Real-time"], p=[0.40, 0.40, 0.20])
    budget_press = rng.choice(["Flexible", "Moderate", "Tight"], p=[0.30, 0.40, 0.30])
    maint_req    = rng.choice(["Low", "Medium", "High"], p=[0.25, 0.45, 0.30])

    c_idx = _score(complexity, "complexity_score")
    r_idx = _score(risk, "technical_risk_level")

    loc       = int(np.clip(rng.lognormal(np.log([2_000, 12_000, 50_000][c_idx]), 0.5), 500, 200_000))
    timeline  = int(np.clip(rng.normal(30 + 60 * c_idx, 20), 7, 365))
    team_size = int(np.clip(rng.normal(2 + 3 * c_idx, 1.5), 1, 20))
    integr    = int(np.clip(rng.poisson(2 + 2 * r_idx), 0, 20))
    test_cov  = float(np.clip(rng.normal(55 + 10 * c_idx, 15), 20, 98))

    reg_prob = 0.15
    if domain in ("Security", "Data"):
        reg_prob += 0.30
    if risk in ("High", "Critical"):
        reg_prob += 0.20
    regulatory = int(rng.random() < reg_prob)

    return {
        "estimated_loc":         loc,
        "complexity_score":      complexity,
        "timeline_days":         timeline,
        "team_size_required":    team_size,
        "domain_category":       domain,
        "technical_risk_level":  risk,
        "integration_count":     integr,
        "seniority_required":    seniority,
        "regulatory_compliance": regulatory,
        "testing_coverage_pct":  round(test_cov, 1),
        "documentation_level":   doc_level,
        "performance_tier":      perf_tier,
        "security_criticality":  security,
        "budget_pressure":       budget_press,
        "maintainability_req":   maint_req,
    }


def _assign_greenfield_labels(df: pd.DataFrame, rng: np.random.Generator) -> None:
    labels = [_greenfield_rule(row) for _, row in df.iterrows()]
    for i in range(len(labels)):
        if rng.random() < 0.05:
            adjacent = {"Human": "Hybrid", "Hybrid": str(rng.choice(["Human", "AI"])), "AI": "Hybrid"}
            labels[i] = adjacent[labels[i]]
    df[TARGET_CLASS] = labels


def _greenfield_rule(row: pd.Series) -> str:
    sec  = row["security_criticality"]
    risk = row["technical_risk_level"]
    comp = row["complexity_score"]
    reg  = row["regulatory_compliance"]
    sen  = row["seniority_required"]
    bud  = row["budget_pressure"]
    loc  = row["estimated_loc"]
    perf = row["performance_tier"]

    if reg == 1 and risk in ("High", "Critical"):    return "Human"
    if sec == "Critical":                             return "Human"
    if sec == "High" and risk in ("High", "Critical"): return "Human"
    if risk == "Critical":                            return "Human"
    if comp == "High" and sen == "Architect":         return "Human"
    if perf == "Real-time" and risk == "Critical":    return "Human"
    if loc > 60_000 and comp == "High":               return "Human"

    if comp == "Low" and risk in ("Low", "Medium") and sec in ("Low", "Medium") and reg == 0 and loc < 10_000:
        return "AI"
    if bud == "Tight" and comp == "Low" and risk == "Low":
        return "AI"
    if comp == "Low" and sen in ("Junior", "Mid") and risk == "Low" and reg == 0:
        return "AI"

    return "Hybrid"


def _assign_greenfield_margin(df: pd.DataFrame, rng: np.random.Generator) -> None:
    margins = []
    for _, row in df.iterrows():
        complexity = _score(row["complexity_score"],     "complexity_score")     / 2.0
        risk       = _score(row["technical_risk_level"], "technical_risk_level") / 3.0
        security   = _score(row["security_criticality"], "security_criticality") / 3.0
        seniority  = _score(row["seniority_required"],   "seniority_required")   / 3.0
        doc        = _score(row["documentation_level"],  "documentation_level")  / 2.0
        perf       = _score(row["performance_tier"],     "performance_tier")     / 2.0
        maint      = _score(row["maintainability_req"],  "maintainability_req")  / 2.0
        budget_bp  = _score(row["budget_pressure"],      "budget_pressure")      / 2.0
        loc_norm   = np.log1p(row["estimated_loc"]) / np.log1p(200_000)
        team_norm  = row["team_size_required"] / 20.0
        integ_n    = row["integration_count"] / 20.0
        test_n     = row["testing_coverage_pct"] / 100.0
        reg        = float(row["regulatory_compliance"])

        labour_cost     = 30 + 20 * seniority + 10 * team_norm + 5 * loc_norm
        risk_cost       = 5 * risk + 5 * security + 3 * reg + 2 * integ_n
        overhead        = 4 * doc + 3 * test_n + 3 * perf + 2 * maint
        complexity_cost = 10 * complexity
        budget_benefit  = 5 * budget_bp

        margin = 100.0 - (labour_cost + risk_cost + overhead + complexity_cost) + budget_benefit
        margin += rng.normal(0, 1.5)
        margins.append(round(float(np.clip(margin, 0.0, 75.0)), 2))
    df[TARGET_REGR] = margins


# ===========================================================================
# LEGACY
# ===========================================================================

def synthesise_legacy(n: int = N_SAMPLES, seed: int = SEED + 1) -> pd.DataFrame:
    """800 synthetic legacy system project records (Sprint Two)."""
    rng = np.random.default_rng(seed)
    rows = [_make_legacy_record(rng) for _ in range(n)]
    df = pd.DataFrame(rows)
    df["project_type"] = 1   # 1 = Legacy
    _assign_legacy_labels(df, rng)
    _assign_legacy_margin(df, rng)
    return df


def _make_legacy_record(rng: np.random.Generator) -> dict:
    # Shared features — legacy projects tend toward higher complexity/risk
    complexity   = rng.choice(["Low", "Medium", "High"], p=[0.15, 0.40, 0.45])
    risk         = rng.choice(["Low", "Medium", "High", "Critical"], p=[0.15, 0.30, 0.40, 0.15])
    security     = rng.choice(["Low", "Medium", "High", "Critical"], p=[0.15, 0.35, 0.35, 0.15])
    seniority    = rng.choice(["Junior", "Mid", "Senior", "Architect"], p=[0.10, 0.30, 0.45, 0.15])
    domain       = rng.choice(DOMAIN_CATEGORIES, p=[0.25, 0.25, 0.15, 0.25, 0.10])
    doc_level    = rng.choice(["Minimal", "Standard", "Comprehensive"], p=[0.30, 0.50, 0.20])
    perf_tier    = rng.choice(["Standard", "High", "Real-time"], p=[0.35, 0.40, 0.25])
    budget_press = rng.choice(["Flexible", "Moderate", "Tight"], p=[0.25, 0.35, 0.40])
    maint_req    = rng.choice(["Low", "Medium", "High"], p=[0.15, 0.40, 0.45])

    c_idx = _score(complexity, "complexity_score")
    r_idx = _score(risk, "technical_risk_level")

    # Legacy codebases are typically larger
    loc       = int(np.clip(rng.lognormal(np.log([15_000, 60_000, 200_000][c_idx]), 0.5), 5_000, 500_000))
    timeline  = int(np.clip(rng.normal(45 + 60 * c_idx, 25), 14, 365))
    team_size = int(np.clip(rng.normal(3 + 3 * c_idx, 2.0), 1, 20))
    integr    = int(np.clip(rng.poisson(4 + 3 * r_idx), 0, 20))
    test_cov  = float(np.clip(rng.normal(40 + 8 * c_idx, 18), 5, 90))

    reg_prob = 0.20
    if domain in ("Security", "Data"):
        reg_prob += 0.30
    if risk in ("High", "Critical"):
        reg_prob += 0.25
    regulatory = int(rng.random() < reg_prob)

    # Legacy-specific features
    debt         = rng.choice(["Low", "Medium", "High", "Critical"], p=[0.20, 0.30, 0.30, 0.20])
    doc_quality  = rng.choice(["Poor", "Minimal", "Standard", "Good"], p=[0.25, 0.35, 0.25, 0.15])
    lang_mod     = rng.choice(["Legacy", "Dated", "Modern", "Current"], p=[0.15, 0.30, 0.35, 0.20])
    familiarity  = rng.choice(["Unfamiliar", "Low", "Medium", "High"], p=[0.08, 0.25, 0.42, 0.25])

    # Codebase age correlated with tech debt and language modernity
    debt_idx     = _score(debt, "technical_debt_score")
    lang_idx     = 3 - _score(lang_mod, "language_modernity")   # inverted: Legacy=3, Current=0
    age_base     = 3 + 4 * debt_idx + 2 * lang_idx
    age          = int(np.clip(rng.normal(age_base, 3), 1, 30))

    dep_count    = int(np.clip(rng.lognormal(np.log(50 + 30 * debt_idx), 0.6), 10, 500))
    last_refact  = int(np.clip(rng.normal(2 + 2 * debt_idx, 2), 0, 15))
    incident_rt  = float(np.clip(rng.exponential(1 + 2 * debt_idx + r_idx), 0, 20))
    duplication  = float(np.clip(rng.normal(10 + 12 * debt_idx, 8), 0, 60))
    exist_test   = float(np.clip(rng.normal(65 - 12 * debt_idx, 15), 5, 85))

    return {
        "estimated_loc":              loc,
        "complexity_score":           complexity,
        "timeline_days":              timeline,
        "team_size_required":         team_size,
        "domain_category":            domain,
        "technical_risk_level":       risk,
        "integration_count":          integr,
        "seniority_required":         seniority,
        "regulatory_compliance":      regulatory,
        "testing_coverage_pct":       round(test_cov, 1),
        "documentation_level":        doc_level,
        "performance_tier":           perf_tier,
        "security_criticality":       security,
        "budget_pressure":            budget_press,
        "maintainability_req":        maint_req,
        # legacy-specific
        "technical_debt_score":       debt,
        "documentation_quality":      doc_quality,
        "language_modernity":         lang_mod,
        "team_familiarity":           familiarity,
        "codebase_age_years":         age,
        "existing_test_coverage_pct": round(exist_test, 1),
        "dependency_count":           dep_count,
        "last_refactor_years":        last_refact,
        "incident_rate_monthly":      round(incident_rt, 2),
        "code_duplication_pct":       round(duplication, 1),
    }


def _assign_legacy_labels(df: pd.DataFrame, rng: np.random.Generator) -> None:
    labels = [_legacy_rule(row) for _, row in df.iterrows()]
    for i in range(len(labels)):
        if rng.random() < 0.05:
            adjacent = {"Human": "Hybrid", "Hybrid": str(rng.choice(["Human", "AI"])), "AI": "Hybrid"}
            labels[i] = adjacent[labels[i]]
    df[TARGET_CLASS] = labels


def _legacy_rule(row: pd.Series) -> str:
    """
    Legacy label rules extend greenfield rules with debt/familiarity/modernity signals.

    Key differences vs greenfield:
    - High technical debt + old codebase heavily favours Human (comprehension debt)
    - Poor documentation quality + low team familiarity → Human (knowledge gap)
    - Legacy/Dated language modernity → Human (AI training data thin for old stacks)
    - Low debt + modern stack + high familiarity → AI feasible even at medium complexity
    """
    sec    = row["security_criticality"]
    risk   = row["technical_risk_level"]
    comp   = row["complexity_score"]
    reg    = row["regulatory_compliance"]
    sen    = row["seniority_required"]
    bud    = row["budget_pressure"]
    loc    = row["estimated_loc"]
    perf   = row["performance_tier"]
    debt   = row["technical_debt_score"]
    doc_q  = row["documentation_quality"]
    lang   = row["language_modernity"]
    fam    = row["team_familiarity"]
    age    = row["codebase_age_years"]
    inc    = row["incident_rate_monthly"]
    dup    = row["code_duplication_pct"]

    # ── HUMAN (safety, compliance, debt, unfamiliarity) ──────────────────────
    if reg == 1 and risk in ("High", "Critical"):          return "Human"
    if sec == "Critical":                                   return "Human"
    if sec == "High" and risk in ("High", "Critical"):      return "Human"
    if risk == "Critical":                                  return "Human"
    if debt == "Critical":                                  return "Human"
    if debt == "High" and fam in ("Unfamiliar", "Low"):           return "Human"
    if lang == "Legacy" and comp in ("Medium", "High"):     return "Human"
    if doc_q == "Poor" and fam in ("Unfamiliar", "Low") and comp == "High": return "Human"
    if age > 15 and debt in ("High", "Critical"):           return "Human"
    if inc > 10 and risk in ("High", "Critical"):           return "Human"
    if comp == "High" and sen == "Architect":               return "Human"
    if dup > 40 and comp == "High":                         return "Human"
    if loc > 150_000 and debt in ("High", "Critical"):      return "Human"

    # ── AI (modern stack, low debt, familiar team, low risk) ─────────────────
    if (comp == "Low"
            and debt in ("Low", "Medium")
            and lang in ("Modern", "Current")
            and fam in ("Medium", "High")
            and risk in ("Low", "Medium")
            and reg == 0):
        return "AI"
    if (bud == "Tight"
            and comp in ("Low", "Medium")
            and debt == "Low"
            and lang in ("Modern", "Current")
            and fam == "High"
            and risk == "Low"):
        return "AI"

    # ── HYBRID ───────────────────────────────────────────────────────────────
    return "Hybrid"


def _assign_legacy_margin(df: pd.DataFrame, rng: np.random.Generator) -> None:
    """
    Legacy margin formula adds debt-servicing cost, incident remediation cost,
    and a familiarity/knowledge-transfer premium on top of the greenfield formula.
    """
    margins = []
    for _, row in df.iterrows():
        complexity = _score(row["complexity_score"],     "complexity_score")     / 2.0
        risk       = _score(row["technical_risk_level"], "technical_risk_level") / 3.0
        security   = _score(row["security_criticality"], "security_criticality") / 3.0
        seniority  = _score(row["seniority_required"],   "seniority_required")   / 3.0
        doc        = _score(row["documentation_level"],  "documentation_level")  / 2.0
        perf       = _score(row["performance_tier"],     "performance_tier")     / 2.0
        maint      = _score(row["maintainability_req"],  "maintainability_req")  / 2.0
        budget_bp  = _score(row["budget_pressure"],      "budget_pressure")      / 2.0
        debt       = _score(row["technical_debt_score"], "technical_debt_score") / 3.0
        doc_q_inv  = (3 - _score(row["documentation_quality"], "documentation_quality")) / 3.0  # poor=high cost
        lang_inv   = (3 - _score(row["language_modernity"],    "language_modernity"))    / 3.0  # legacy=high cost
        fam_inv    = (3 - _score(row["team_familiarity"],       "team_familiarity"))      / 3.0  # none=high cost

        loc_norm  = np.log1p(row["estimated_loc"]) / np.log1p(500_000)
        team_norm = row["team_size_required"] / 20.0
        integ_n   = row["integration_count"] / 20.0
        test_n    = row["testing_coverage_pct"] / 100.0
        reg       = float(row["regulatory_compliance"])
        inc_n     = min(row["incident_rate_monthly"] / 20.0, 1.0)
        dup_n     = row["code_duplication_pct"] / 60.0

        labour_cost     = 30 + 20 * seniority + 10 * team_norm + 5 * loc_norm
        risk_cost       = 5 * risk + 5 * security + 3 * reg + 2 * integ_n
        overhead        = 4 * doc + 3 * test_n + 3 * perf + 2 * maint
        complexity_cost = 10 * complexity
        budget_benefit  = 5 * budget_bp

        # Legacy-specific additional costs
        debt_cost       = 8 * debt          # tech debt servicing
        incident_cost   = 6 * inc_n         # incident remediation
        familiarity_cost = 4 * fam_inv      # knowledge-transfer overhead
        lang_cost       = 3 * lang_inv      # old-stack tooling premium
        doc_quality_cost = 2 * doc_q_inv    # documentation gap surcharge
        dup_cost        = 2 * dup_n         # duplication rework cost

        legacy_overhead = debt_cost + incident_cost + familiarity_cost + lang_cost + doc_quality_cost + dup_cost

        margin = 100.0 - (labour_cost + risk_cost + overhead + complexity_cost + legacy_overhead) + budget_benefit
        margin += rng.normal(0, 1.5)
        margins.append(round(float(np.clip(margin, 2.0, 70.0)), 2))
    df[TARGET_REGR] = margins


# ===========================================================================
# Combined dataset
# ===========================================================================

def synthesise_combined(n_each: int = N_SAMPLES, seed: int = SEED) -> pd.DataFrame:
    """Return unified DataFrame: n_each Greenfield + n_each Legacy records."""
    gf = synthesise_greenfield(n_each, seed=seed)
    lg = synthesise_legacy(n_each, seed=seed + 1)
    df = pd.concat([gf, lg], ignore_index=True)
    # Shuffle so rows aren't type-sorted
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    return df


def save_dataset(df: pd.DataFrame, log: bool = True) -> Path:
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    out = DATA_PROCESSED / "combined_features.csv"
    df.to_csv(out, index=False)

    if log:
        DATA_SYNTHETIC.mkdir(parents=True, exist_ok=True)
        meta = {
            "generated_at":   datetime.now(timezone.utc).isoformat(),
            "n_total":        len(df),
            "n_greenfield":   int((df["project_type"] == 0).sum()),
            "n_legacy":       int((df["project_type"] == 1).sum()),
            "seed":           SEED,
            "label_dist_overall":     df[TARGET_CLASS].value_counts().to_dict(),
            "label_dist_greenfield":  df[df["project_type"] == 0][TARGET_CLASS].value_counts().to_dict(),
            "label_dist_legacy":      df[df["project_type"] == 1][TARGET_CLASS].value_counts().to_dict(),
            "profit_margin_stats": {
                "mean": round(float(df[TARGET_REGR].mean()), 2),
                "std":  round(float(df[TARGET_REGR].std()),  2),
                "min":  round(float(df[TARGET_REGR].min()),  2),
                "max":  round(float(df[TARGET_REGR].max()),  2),
            },
        }
        with open(DATA_SYNTHETIC / "synthesis_log.json", "w") as f:
            json.dump(meta, f, indent=2)

    return out


# ===========================================================================
# CLI
# ===========================================================================

if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else N_SAMPLES
    df = synthesise_combined(n)
    out = save_dataset(df)
    print(f"Combined dataset saved → {out}  ({len(df)} total records)")
    print(f"\nGreenfield ({(df['project_type']==0).sum()}):")
    print(df[df["project_type"] == 0][TARGET_CLASS].value_counts().to_string())
    print(f"\nLegacy ({(df['project_type']==1).sum()}):")
    print(df[df["project_type"] == 1][TARGET_CLASS].value_counts().to_string())
    print(f"\nProfit margin  mean={df[TARGET_REGR].mean():.1f}%  "
          f"std={df[TARGET_REGR].std():.1f}%  "
          f"range=[{df[TARGET_REGR].min():.1f}, {df[TARGET_REGR].max():.1f}]")
