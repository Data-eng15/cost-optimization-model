"""Unit tests for data validation helpers in utils.py"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd
import pytest

from utils import validate_dataframe, record_to_dataframe
from config import DATASET_PATH, ALL_FEATURES


class TestValidateDataframe:
    def test_clean_dataset_passes(self):
        df = pd.read_csv(DATASET_PATH)
        errors = validate_dataframe(df)
        assert errors == [], f"Unexpected validation errors: {errors}"

    def test_missing_value_detected(self):
        df = pd.read_csv(DATASET_PATH).copy()
        df.loc[0, "estimated_loc"] = None
        errors = validate_dataframe(df)
        assert any("estimated_loc" in e for e in errors)

    def test_negative_numeric_detected(self):
        df = pd.read_csv(DATASET_PATH).copy()
        df.loc[0, "timeline_days"] = -5
        errors = validate_dataframe(df)
        assert any("timeline_days" in e for e in errors)

    def test_invalid_ordinal_detected(self):
        df = pd.read_csv(DATASET_PATH).copy()
        df.loc[0, "complexity_score"] = "VeryHigh"
        errors = validate_dataframe(df)
        assert any("complexity_score" in e for e in errors)

    def test_invalid_binary_detected(self):
        df = pd.read_csv(DATASET_PATH).copy()
        df.loc[0, "regulatory_compliance"] = 2
        errors = validate_dataframe(df)
        assert any("regulatory_compliance" in e for e in errors)

    def test_invalid_domain_detected(self):
        df = pd.read_csv(DATASET_PATH).copy()
        df.loc[0, "domain_category"] = "Quantum"
        errors = validate_dataframe(df)
        assert any("domain" in e.lower() for e in errors)


class TestRecordToDataframe:
    def _valid_greenfield(self):
        return {
            "project_type":          0,
            "estimated_loc":         5_000,
            "complexity_score":      "Medium",
            "timeline_days":         45,
            "team_size_required":    3,
            "domain_category":       "Web",
            "technical_risk_level":  "Low",
            "integration_count":     2,
            "seniority_required":    "Mid",
            "regulatory_compliance": 0,
            "testing_coverage_pct":  70.0,
            "documentation_level":   "Standard",
            "performance_tier":      "Standard",
            "security_criticality":  "Low",
            "budget_pressure":       "Moderate",
            "maintainability_req":   "Medium",
        }

    def _valid_legacy(self):
        return {
            "project_type":               1,
            "estimated_loc":              30_000,
            "complexity_score":           "Medium",
            "timeline_days":              60,
            "team_size_required":         4,
            "domain_category":            "Data",
            "technical_risk_level":       "Medium",
            "integration_count":          5,
            "seniority_required":         "Senior",
            "regulatory_compliance":      0,
            "testing_coverage_pct":       55.0,
            "documentation_level":        "Standard",
            "performance_tier":           "High",
            "security_criticality":       "Medium",
            "budget_pressure":            "Moderate",
            "maintainability_req":        "High",
            "technical_debt_score":       "Medium",
            "documentation_quality":      "Minimal",
            "language_modernity":         "Modern",
            "team_familiarity":           "Medium",
            "codebase_age_years":         6,
            "existing_test_coverage_pct": 50.0,
            "dependency_count":           80,
            "last_refactor_years":        3,
            "incident_rate_monthly":      2.0,
            "code_duplication_pct":       15.0,
        }

    def test_valid_greenfield_passes(self):
        df = record_to_dataframe(self._valid_greenfield())
        assert list(df.columns) == ALL_FEATURES
        assert len(df) == 1

    def test_valid_legacy_passes(self):
        df = record_to_dataframe(self._valid_legacy())
        assert list(df.columns) == ALL_FEATURES
        assert len(df) == 1

    def test_greenfield_legacy_defaults_auto_applied(self):
        """Greenfield record without legacy fields gets defaults automatically."""
        r = self._valid_greenfield()
        df = record_to_dataframe(r)
        assert df["codebase_age_years"].iloc[0] == 0
        assert df["technical_debt_score"].iloc[0] == "Low"

    def test_invalid_complexity_raises(self):
        r = self._valid_greenfield()
        r["complexity_score"] = "Extreme"
        with pytest.raises(ValueError):
            record_to_dataframe(r)

    def test_invalid_legacy_debt_raises(self):
        r = self._valid_legacy()
        r["technical_debt_score"] = "Astronomical"
        with pytest.raises(ValueError):
            record_to_dataframe(r)

    def test_invalid_project_type_raises(self):
        r = self._valid_greenfield()
        r["project_type"] = 5
        with pytest.raises(ValueError):
            record_to_dataframe(r)
