"""
TCO Optimisation — FastAPI inference endpoint.

Run with:
    uvicorn app.api:app --reload --port 8000
    # or from project root:
    PYTHONPATH=src uvicorn app.api:app --reload --port 8000

Endpoints:
    POST /predict   — team recommendation + profit margin
    GET  /health    — liveness check
    GET  /metadata  — model metrics + feature importances
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import CLASS_LABELS, METADATA_PATH, MODELS_DIR
from utils import load_model, load_json, record_to_dataframe
from model import predict

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="TCO Optimisation API",
    description="Predict optimal team composition (Human/Hybrid/AI) and profit margin for software projects.",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Load artefacts once at startup
# ---------------------------------------------------------------------------
try:
    _clf = load_model(MODELS_DIR / "xgboost_classifier.pkl")
    _rgr = load_model(MODELS_DIR / "stacking_regressor.pkl")
    _meta = load_json(METADATA_PATH)
except Exception as e:
    raise RuntimeError(f"Failed to load model artefacts: {e}")


# ---------------------------------------------------------------------------
# Request schema — all 29 features
# ---------------------------------------------------------------------------
class ProjectInput(BaseModel):
    # Discriminator
    project_type: int = Field(..., ge=0, le=1, description="0=Greenfield, 1=Legacy")

    # Shared numeric
    estimated_loc:         int   = Field(..., ge=100,  le=500_000)
    timeline_days:         int   = Field(..., ge=7,    le=365)
    team_size_required:    int   = Field(..., ge=1,    le=20)
    integration_count:     int   = Field(..., ge=0,    le=20)
    testing_coverage_pct:  float = Field(..., ge=0,    le=100)

    # Shared ordinal
    complexity_score:      str = Field(..., pattern="^(Low|Medium|High)$")
    technical_risk_level:  str = Field(..., pattern="^(Low|Medium|High|Critical)$")
    seniority_required:    str = Field(..., pattern="^(Junior|Mid|Senior|Architect)$")
    documentation_level:   str = Field(..., pattern="^(Minimal|Standard|Comprehensive)$")
    performance_tier:      str = Field(..., pattern="^(Standard|High|Real-time)$")
    security_criticality:  str = Field(..., pattern="^(Low|Medium|High|Critical)$")
    budget_pressure:       str = Field(..., pattern="^(Flexible|Moderate|Tight)$")
    maintainability_req:   str = Field(..., pattern="^(Low|Medium|High)$")

    # Shared binary / nominal
    regulatory_compliance: int  = Field(..., ge=0, le=1)
    domain_category:       str  = Field(..., pattern="^(Web|Infrastructure|Security|Data|Mobile)$")

    # Legacy-specific numeric (defaults match GREENFIELD_LEGACY_DEFAULTS)
    codebase_age_years:          int   = Field(default=0,   ge=0,  le=30)
    existing_test_coverage_pct:  float = Field(default=0.0, ge=0,  le=100)
    dependency_count:            int   = Field(default=0,   ge=0,  le=500)
    last_refactor_years:         int   = Field(default=0,   ge=0,  le=15)
    incident_rate_monthly:       float = Field(default=0.0, ge=0,  le=20)
    code_duplication_pct:        float = Field(default=0.0, ge=0,  le=60)

    # Legacy-specific ordinal
    technical_debt_score:  str = Field(default="Low",     pattern="^(Low|Medium|High|Critical)$")
    documentation_quality: str = Field(default="Poor",    pattern="^(Poor|Minimal|Standard|Good)$")
    language_modernity:    str = Field(default="Current", pattern="^(Legacy|Dated|Modern|Current)$")
    team_familiarity:      str = Field(default="High",    pattern="^(Unfamiliar|Low|Medium|High)$")

    class Config:
        json_schema_extra = {
            "example": {
                "project_type": 0,
                "estimated_loc": 8000,
                "timeline_days": 60,
                "team_size_required": 3,
                "integration_count": 2,
                "testing_coverage_pct": 70.0,
                "complexity_score": "Medium",
                "technical_risk_level": "Low",
                "seniority_required": "Mid",
                "documentation_level": "Standard",
                "performance_tier": "Standard",
                "security_criticality": "Medium",
                "budget_pressure": "Moderate",
                "maintainability_req": "Medium",
                "regulatory_compliance": 0,
                "domain_category": "Web",
            }
        }


# ---------------------------------------------------------------------------
# Response schema
# ---------------------------------------------------------------------------
class PredictionResponse(BaseModel):
    recommended_team:            str
    probabilities:               dict[str, float]
    predicted_profit_margin_pct: float
    nfr06_triggered:             bool
    confidence:                  str   # High / Medium / Low


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok", "model_version": _meta.get("version", "unknown")}


@app.get("/metadata")
def metadata():
    return {
        "version":                  _meta.get("version"),
        "classification_metrics":   _meta.get("classification_metrics"),
        "regression_metrics":       _meta.get("regression_metrics"),
        "feature_importance":       _meta.get("feature_importance"),
        "class_labels":             CLASS_LABELS,
        "base_learner_breakdown":   _meta.get("base_learner_breakdown"),
    }


@app.post("/predict", response_model=PredictionResponse)
def predict_team(project: ProjectInput):
    try:
        record = project.model_dump()
        X      = record_to_dataframe(record)
        result = predict(_clf, _rgr, X)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    rec   = result["recommended_team"]
    probs = result["probabilities"]
    top_p = max(probs.values())

    nfr06 = (
        project.technical_risk_level == "Critical"
        or project.security_criticality == "Critical"
    )

    confidence = "High" if top_p >= 0.80 else "Medium" if top_p >= 0.60 else "Low"

    return PredictionResponse(
        recommended_team=rec,
        probabilities=probs,
        predicted_profit_margin_pct=result["predicted_profit_margin_pct"],
        nfr06_triggered=nfr06,
        confidence=confidence,
    )
