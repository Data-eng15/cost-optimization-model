"""
TCO Optimisation Dashboard — Streamlit application.
Covers both Greenfield (Sprint One) and Legacy (Sprint Two) projects.

Run with:
    streamlit run app/dashboard.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from config import (
    CLASS_LABELS, DATASET_PATH, DOMAIN_CATEGORIES, GREENFIELD_LEGACY_DEFAULTS,
    LEGACY_ORDINAL_FEATURES, METADATA_PATH, MODELS_DIR, ORDINAL_FEATURES,
)
from utils import load_model, load_json, record_to_dataframe
from model import predict, extract_feature_importance

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="TCO Optimisation Model",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Load artefacts (cached)
# ---------------------------------------------------------------------------
@st.cache_resource
def load_artefacts():
    clf  = load_model(MODELS_DIR / "xgboost_classifier.pkl")
    rgr  = load_model(MODELS_DIR / "random_forest_classifier.pkl")
    meta = load_json(METADATA_PATH)
    return clf, rgr, meta

clf_pipe, rgr_pipe, metadata = load_artefacts()

# ---------------------------------------------------------------------------
# Sidebar — project type selector + input form
# ---------------------------------------------------------------------------
st.sidebar.title("Project Configuration")

project_type_label = st.sidebar.radio(
    "Project Type",
    ["Greenfield", "Legacy"],
    horizontal=True,
    help="Greenfield = new build from scratch. Legacy = existing codebase (maintenance, extension, modernisation).",
)
is_legacy = project_type_label == "Legacy"

st.sidebar.markdown("---")

with st.sidebar.form("project_form"):

    # ── Shared fields ────────────────────────────────────────────────────────
    st.subheader("Scale & Scope")
    estimated_loc      = st.number_input("Estimated LOC",        min_value=100,   max_value=500_000, value=15_000 if is_legacy else 8_000, step=500)
    timeline_days      = st.number_input("Timeline (days)",      min_value=7,     max_value=365,     value=90    if is_legacy else 60,    step=1)
    team_size_required = st.number_input("Team Size Required",   min_value=1,     max_value=20,      value=4     if is_legacy else 3,     step=1)
    integration_count  = st.number_input("External Integrations",min_value=0,     max_value=20,      value=5     if is_legacy else 2,     step=1)
    testing_coverage   = st.slider("Expected Test Coverage (%)", min_value=5,     max_value=98,      value=60    if is_legacy else 70)

    st.subheader("Project Characteristics")
    complexity_score     = st.selectbox("Complexity",           ORDINAL_FEATURES["complexity_score"],     index=1)
    technical_risk_level = st.selectbox("Technical Risk",       ORDINAL_FEATURES["technical_risk_level"], index=1)
    security_criticality = st.selectbox("Security Criticality", ORDINAL_FEATURES["security_criticality"], index=1)
    seniority_required   = st.selectbox("Seniority Required",   ORDINAL_FEATURES["seniority_required"],   index=2)
    domain_category      = st.selectbox("Domain",               DOMAIN_CATEGORIES,                        index=0)

    st.subheader("Constraints")
    regulatory_compliance = st.checkbox("Regulatory Compliance Required")
    documentation_level   = st.selectbox("Documentation Level", ORDINAL_FEATURES["documentation_level"],  index=1)
    performance_tier      = st.selectbox("Performance Tier",    ORDINAL_FEATURES["performance_tier"],     index=0)
    budget_pressure       = st.selectbox("Budget Pressure",     ORDINAL_FEATURES["budget_pressure"],      index=1)
    maintainability_req   = st.selectbox("Maintainability",     ORDINAL_FEATURES["maintainability_req"],  index=1)

    # ── Legacy-only fields ────────────────────────────────────────────────────
    if is_legacy:
        st.markdown("---")
        st.subheader("Legacy Codebase Details")
        technical_debt_score       = st.selectbox("Technical Debt",          LEGACY_ORDINAL_FEATURES["technical_debt_score"],  index=1)
        documentation_quality      = st.selectbox("Existing Doc Quality",    LEGACY_ORDINAL_FEATURES["documentation_quality"], index=1)
        language_modernity         = st.selectbox("Language / Stack Modernity", LEGACY_ORDINAL_FEATURES["language_modernity"], index=1)
        team_familiarity           = st.selectbox("Team Familiarity",         LEGACY_ORDINAL_FEATURES["team_familiarity"],      index=2)
        codebase_age_years         = st.number_input("Codebase Age (years)", min_value=1, max_value=30,  value=8,   step=1)
        existing_test_coverage_pct = st.slider("Existing Test Coverage (%)", min_value=0, max_value=90,  value=45)
        dependency_count           = st.number_input("Dependency Count",     min_value=5, max_value=500, value=80,  step=5)
        last_refactor_years        = st.number_input("Years Since Last Refactor", min_value=0, max_value=15, value=3, step=1)
        incident_rate_monthly      = st.slider("Incidents / Month",          min_value=0, max_value=20,  value=3)
        code_duplication_pct       = st.slider("Code Duplication (%)",       min_value=0, max_value=60,  value=15)

    submitted = st.form_submit_button("Analyse Project", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------
badge_colour = "#1565C0" if not is_legacy else "#6A1B9A"
badge_label  = "Greenfield" if not is_legacy else "Legacy"

st.title("TCO Optimisation Model")
st.markdown(
    f"**Team Composition Decision Support** &nbsp;|&nbsp; "
    f"<span style='background:{badge_colour};color:white;padding:2px 10px;border-radius:12px;"
    f"font-size:0.85rem;'>{badge_label}</span>&nbsp; "
    f"*University of Essex · Soham Nageshkumar Dharne · 2026*",
    unsafe_allow_html=True,
)

tab_predict, tab_compare, tab_model, tab_data = st.tabs(
    ["Prediction", "Greenfield vs Legacy", "Model Performance", "Dataset Explorer"]
)

# ── TAB 1: Prediction ───────────────────────────────────────────────────────
with tab_predict:
    if not submitted:
        st.info(f"Configure your **{project_type_label}** project in the sidebar and click **Analyse Project**.")
        st.image(str(Path(__file__).parents[1] / "results" / "visualizations" / "feature_importance.png"),
                 caption="XGBoost feature importances (combined dataset)", use_container_width=True)
    else:
        record = {
            "project_type":          1 if is_legacy else 0,
            "estimated_loc":         estimated_loc,
            "complexity_score":      complexity_score,
            "timeline_days":         timeline_days,
            "team_size_required":    team_size_required,
            "domain_category":       domain_category,
            "technical_risk_level":  technical_risk_level,
            "integration_count":     integration_count,
            "seniority_required":    seniority_required,
            "regulatory_compliance": int(regulatory_compliance),
            "testing_coverage_pct":  float(testing_coverage),
            "documentation_level":   documentation_level,
            "performance_tier":      performance_tier,
            "security_criticality":  security_criticality,
            "budget_pressure":       budget_pressure,
            "maintainability_req":   maintainability_req,
        }
        if is_legacy:
            record.update({
                "technical_debt_score":       technical_debt_score,
                "documentation_quality":      documentation_quality,
                "language_modernity":         language_modernity,
                "team_familiarity":           team_familiarity,
                "codebase_age_years":         int(codebase_age_years),
                "existing_test_coverage_pct": float(existing_test_coverage_pct),
                "dependency_count":           int(dependency_count),
                "last_refactor_years":        int(last_refactor_years),
                "incident_rate_monthly":      float(incident_rate_monthly),
                "code_duplication_pct":       float(code_duplication_pct),
            })

        try:
            X      = record_to_dataframe(record)
            result = predict(clf_pipe, rgr_pipe, X)
        except Exception as e:
            st.error(f"Prediction error: {e}")
            st.stop()

        rec    = result["recommended_team"]
        prob   = result["probabilities"]
        margin = result["predicted_profit_margin_pct"]

        colour = {"Human": "#EF5350", "Hybrid": "#FFA726", "AI": "#42A5F5"}[rec]
        icon   = {"Human": "👷", "Hybrid": "🤝", "AI": "🤖"}[rec]

        st.markdown(
            f"""
            <div style='padding:1.5rem;background:{colour}20;border-left:6px solid {colour};
                        border-radius:8px;margin-bottom:1rem;'>
                <h2 style='margin:0;color:{colour};'>{icon} Recommended: {rec} Team</h2>
                <p style='margin:0.3rem 0 0;color:#555;'>
                    Project type: <strong>{project_type_label}</strong> &nbsp;|&nbsp;
                    Predicted profit margin: <strong>{margin:.1f}%</strong>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Confidence Breakdown")
            proba_df = pd.DataFrame({"Team Type": list(prob.keys()), "Probability": [v * 100 for v in prob.values()]})
            fig = px.bar(proba_df, x="Team Type", y="Probability",
                         color="Team Type",
                         color_discrete_map={"Human": "#EF5350", "Hybrid": "#FFA726", "AI": "#42A5F5"},
                         text_auto=".1f")
            fig.update_layout(yaxis_title="Probability (%)", showlegend=False, yaxis_range=[0, 100], height=350)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Key Decision Drivers")
            fi     = extract_feature_importance(clf_pipe)
            top_fi = dict(list(fi.items())[:12])
            fi_df  = pd.DataFrame({"Feature": list(top_fi.keys())[::-1], "Importance": list(top_fi.values())[::-1]})
            fig2   = px.bar(fi_df, x="Importance", y="Feature", orientation="h",
                            color="Importance", color_continuous_scale="Blues")
            fig2.update_layout(showlegend=False, coloraxis_showscale=False, height=350)
            st.plotly_chart(fig2, use_container_width=True)

        # Context-aware explanation
        explanations = {
            ("Greenfield", "Human"): "This new project has critical safety/compliance signals. AI pipelines carry unacceptable hallucination risk at this scale and risk level.",
            ("Greenfield", "Hybrid"): "A human-AI orchestration maximises throughput on this greenfield project while human oversight manages quality gates and integration risk.",
            ("Greenfield", "AI"): "Ideal for AI-agent autonomy: small, low-risk, non-regulated, budget-constrained. AI marginal cost (~INR 100/1K LOC) strongly beats human alternatives here.",
            ("Legacy", "Human"): "Legacy projects with high technical debt, poor documentation, or unfamiliar codebases demand human comprehension. AI hallucination risk is amplified by the knowledge gaps in the existing system.",
            ("Legacy", "Hybrid"): "AI agents can accelerate routine refactoring and test generation while humans handle architectural decisions, debt remediation strategy, and tribal knowledge transfer.",
            ("Legacy", "AI"): "Rare for legacy: this codebase has low debt, modern stack, high team familiarity, and low risk — the combination where AI tooling can safely automate maintenance tasks.",
        }
        key = (project_type_label, rec)
        st.info(f"**Why {rec}?** {explanations.get(key, '')}")

        with st.expander("Full input record"):
            st.json(record)

# ── TAB 2: Greenfield vs Legacy Comparison ───────────────────────────────────
with tab_compare:
    st.subheader("How Legacy Differs from Greenfield")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Greenfield TCO drivers:**
        - Complexity & LOC (comprehension debt risk)
        - Security criticality & technical risk
        - Regulatory compliance
        - Performance requirements
        - Team seniority needed
        """)
    with col2:
        st.markdown("""
        **Legacy adds on top:**
        - Technical debt (rework & refactor cost)
        - Documentation quality gap (knowledge transfer overhead)
        - Language/stack modernity (AI training data thinness for old stacks)
        - Team familiarity (onboarding vs. tribal knowledge)
        - Incident rate (ongoing remediation cost)
        - Code duplication (amplifies rework)
        """)

    df = pd.read_csv(DATASET_PATH)
    gf = df[df["project_type"] == 0]
    lg = df[df["project_type"] == 1]

    st.divider()
    st.subheader("Label Distribution Comparison")
    c1, c2 = st.columns(2)
    with c1:
        vc_gf = gf[CLASS_LABELS[0]].value_counts() if CLASS_LABELS[0] in gf.columns else gf["target_team_label"].value_counts()
        vc_gf = gf["target_team_label"].value_counts()
        fig_gf = px.pie(values=vc_gf.values, names=vc_gf.index, title="Greenfield",
                        color=vc_gf.index, color_discrete_map={"Human":"#EF5350","Hybrid":"#FFA726","AI":"#42A5F5"})
        st.plotly_chart(fig_gf, use_container_width=True)
    with c2:
        vc_lg = lg["target_team_label"].value_counts()
        fig_lg = px.pie(values=vc_lg.values, names=vc_lg.index, title="Legacy",
                        color=vc_lg.index, color_discrete_map={"Human":"#EF5350","Hybrid":"#FFA726","AI":"#42A5F5"})
        st.plotly_chart(fig_lg, use_container_width=True)

    st.markdown("> **Insight**: Legacy projects are predominantly Human — high technical debt, old stacks, and poor documentation make pure AI automation a significant reliability risk.")

    st.subheader("Profit Margin Distribution")
    fig_m = px.histogram(df, x="profit_margin_pct", color=df["project_type"].map({0:"Greenfield",1:"Legacy"}),
                         color_discrete_map={"Greenfield":"#1565C0","Legacy":"#6A1B9A"},
                         nbins=40, barmode="overlay", opacity=0.75,
                         labels={"color":"Project Type"},
                         title="Profit Margin: Greenfield vs Legacy")
    st.plotly_chart(fig_m, use_container_width=True)

    st.markdown("> **Insight**: Legacy projects have lower and more compressed profit margins due to the additional debt-servicing, incident remediation, and knowledge-transfer overhead layered on top of standard labour costs.")

# ── TAB 3: Model Performance ─────────────────────────────────────────────────
with tab_model:
    st.subheader("Ensemble Architecture")
    st.markdown("""
    | Layer | Model | Role |
    |---|---|---|
    | Base 1 | XGBoost | Gradient-boosted trees — primary signal |
    | Base 2 | Decision Tree | Interpretable baseline |
    | Base 3 | ANN (128→64→32, ReLU) | Non-linear interactions |
    | Base 4 | Logistic / Linear Regression | Linear baseline + calibration |
    | Meta (Clf) | Logistic Regression | Stacking aggregator |
    | Meta (Rgr) | Ridge Regression | Stacking aggregator |

    Trained on **1,600 records** (800 Greenfield + 800 Legacy). `project_type` is a first-class feature so the model learns type-specific patterns without separate pipelines.
    """)

    clf_test = metadata["classification_metrics"]
    rgr_test = metadata["regression_metrics"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Test Accuracy",   f"{clf_test['accuracy']*100:.1f}%", delta="≥85% target")
    c2.metric("Test F1",         f"{clf_test['f1']*100:.1f}%")
    c3.metric("Test Recall",     f"{clf_test['recall']*100:.1f}%")
    c4.metric("Regression MAPE", f"{rgr_test['mape_pct']:.2f}%",    delta="≤5% target")

    st.divider()
    base = metadata.get("base_learner_breakdown", {})
    if base:
        st.subheader("Base Learner Breakdown (validation set)")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Classification**")
            bdf = pd.DataFrame(base.get("classification", {})).T.reset_index().rename(columns={"index": "Model"})
            bdf["accuracy"] = (bdf["accuracy"] * 100).round(1)
            bdf["f1"]       = (bdf["f1"] * 100).round(1)
            st.dataframe(bdf, hide_index=True, use_container_width=True)
        with c2:
            st.markdown("**Regression**")
            rdf = pd.DataFrame(base.get("regression", {})).T.reset_index().rename(columns={"index": "Model"})
            st.dataframe(rdf, hide_index=True, use_container_width=True)

    st.divider()
    img1, img2 = st.columns(2)
    with img1:
        st.image(str(Path(__file__).parents[1] / "results" / "visualizations" / "confusion_matrix.png"),
                 caption="Test-set confusion matrix", use_container_width=True)
    with img2:
        st.image(str(Path(__file__).parents[1] / "results" / "visualizations" / "feature_importance.png"),
                 caption="XGBoost feature importances", use_container_width=True)

# ── TAB 4: Dataset Explorer ───────────────────────────────────────────────────
with tab_data:
    df = pd.read_csv(DATASET_PATH)
    df["Type"] = df["project_type"].map({0: "Greenfield", 1: "Legacy"})

    st.subheader(f"Combined Dataset: {len(df)} Records")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total",      len(df))
    c2.metric("Greenfield", int((df["project_type"] == 0).sum()))
    c3.metric("Legacy",     int((df["project_type"] == 1).sum()))
    vc = df["target_team_label"].value_counts()
    c4.metric("Human",  int(vc.get("Human",  0)))
    c5.metric("Hybrid", int(vc.get("Hybrid", 0)))

    filter_type = st.radio("Filter by project type", ["All", "Greenfield", "Legacy"], horizontal=True)
    view = df if filter_type == "All" else df[df["Type"] == filter_type]

    c1, c2 = st.columns(2)
    with c1:
        vc2 = view["target_team_label"].value_counts()
        fig = px.pie(values=vc2.values, names=vc2.index, title="Label Distribution",
                     color=vc2.index, color_discrete_map={"Human":"#EF5350","Hybrid":"#FFA726","AI":"#42A5F5"})
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = px.histogram(view, x="profit_margin_pct", color="target_team_label",
                            color_discrete_map={"Human":"#EF5350","Hybrid":"#FFA726","AI":"#42A5F5"},
                            nbins=30, barmode="overlay", opacity=0.75,
                            title="Profit Margin by Team Type")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Feature Distribution")
    shared_feats  = ["complexity_score", "technical_risk_level", "security_criticality",
                     "domain_category", "budget_pressure", "seniority_required"]
    legacy_feats  = ["technical_debt_score", "documentation_quality", "language_modernity", "team_familiarity"]
    feat_opts     = shared_feats + (legacy_feats if filter_type in ["All", "Legacy"] else [])
    feat          = st.selectbox("Select feature", feat_opts)
    fig3 = px.histogram(view, x=feat, color="target_team_label",
                        color_discrete_map={"Human":"#EF5350","Hybrid":"#FFA726","AI":"#42A5F5"},
                        barmode="group", title=f"{feat} by team label")
    st.plotly_chart(fig3, use_container_width=True)

    with st.expander("Raw dataset (first 50 rows)"):
        st.dataframe(view.head(50), use_container_width=True)
