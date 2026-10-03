import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "autopilot.db"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="LLM Cost Autopilot",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def get_connection():
    return sqlite3.connect(DB_PATH)


def load_requests():
    connection = get_connection()

    query = """
        SELECT
            id,
            timestamp,
            complexity_tier,
            classifier_confidence,
            model_name,
            provider,
            model_id,
            input_tokens,
            output_tokens,
            latency_ms,
            cost,
            quality_score,
            escalated,
            escalated_model,
            feedback,
            quality_passed,
            verification_method,
            user_consent,
            original_cost,
            escalated_cost,
            additional_cost,
            total_cost
        FROM requests
        ORDER BY id
    """

    dataframe = pd.read_sql_query(query, connection)

    connection.close()

    return dataframe


# ============================================================
# LOAD DATA
# ============================================================

df = load_requests()


# ============================================================
# HEADER
# ============================================================

st.title("🤖 LLM Cost Autopilot")

st.subheader("Cost Optimization & Model Routing Dashboard")

st.caption(
    "Analytics based on requests stored in the LLM Cost Autopilot SQLite database."
)


# ============================================================
# EMPTY DATABASE CHECK
# ============================================================

if df.empty:
    st.warning("No request records found in the database.")
    st.stop()


# ============================================================
# BASIC METRICS
# ============================================================

total_requests = len(df)

total_cost = df["cost"].fillna(0).sum()

average_cost = (
    df["cost"].fillna(0).mean()
    if total_requests > 0
    else 0
)


# ============================================================
# ALL-SONNET BASELINE
# ============================================================

SONNET_INPUT_COST_PER_MILLION = 3.0
SONNET_OUTPUT_COST_PER_MILLION = 15.0


def calculate_sonnet_cost(row):
    input_cost = (
        (row["input_tokens"] or 0)
        / 1_000_000
        * SONNET_INPUT_COST_PER_MILLION
    )

    output_cost = (
        (row["output_tokens"] or 0)
        / 1_000_000
        * SONNET_OUTPUT_COST_PER_MILLION
    )

    return input_cost + output_cost


df["sonnet_baseline_cost"] = df.apply(
    calculate_sonnet_cost,
    axis=1
)

all_sonnet_cost = df["sonnet_baseline_cost"].sum()

estimated_savings = all_sonnet_cost - total_cost

cost_reduction = (
    (estimated_savings / all_sonnet_cost) * 100
    if all_sonnet_cost > 0
    else 0
)


# ============================================================
# TOP METRIC CARDS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Requests",
        total_requests
    )

with col2:
    st.metric(
        "Dynamic Routing Cost",
        f"${total_cost:.6f}"
    )

with col3:
    st.metric(
        "Estimated Savings",
        f"${estimated_savings:.6f}"
    )

with col4:
    st.metric(
        "Cost Reduction",
        f"{cost_reduction:.2f}%"
    )


st.divider()


# ============================================================
# MODEL-WISE ANALYSIS
# ============================================================

st.header("Model-Wise Analysis")

model_summary = (
    df.groupby("model_name")
    .agg(
        requests=("id", "count"),
        total_cost=("cost", "sum"),
        average_cost=("cost", "mean")
    )
    .reset_index()
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Cost by Model")

    fig = px.bar(
        model_summary,
        x="model_name",
        y="total_cost",
        labels={
            "model_name": "Model",
            "total_cost": "Cost (USD)"
        }
    )

    fig.update_layout(
        dragmode=False,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "scrollZoom": False,
            "displayModeBar": False
        }
    )

with col2:
    st.subheader("Requests by Model")

    fig = px.bar(
        model_summary,
        x="model_name",
        y="requests",
        labels={
            "model_name": "Model",
            "requests": "Requests"
        }
    )

    fig.update_layout(
        dragmode=False,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "scrollZoom": False,
            "displayModeBar": False
        }
    )


st.dataframe(
    model_summary,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# COMPLEXITY-TIER ANALYSIS
# ============================================================

st.header("Complexity-Tier Analysis")

tier_summary = (
    df.groupby("complexity_tier")
    .agg(
        requests=("id", "count"),
        total_cost=("cost", "sum"),
        average_cost=("cost", "mean")
    )
    .reset_index()
)

tier_summary["complexity_tier"] = (
    "Tier " +
    tier_summary["complexity_tier"].astype(str)
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Cost by Complexity Tier")

    fig = px.bar(
        tier_summary,
        x="complexity_tier",
        y="total_cost",
        labels={
            "complexity_tier": "Complexity Tier",
            "total_cost": "Cost (USD)"
        }
    )

    fig.update_layout(
        dragmode=False,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "scrollZoom": False,
            "displayModeBar": False
        }
    )

with col2:
    st.subheader("Requests by Complexity Tier")

    fig = px.bar(
        tier_summary,
        x="complexity_tier",
        y="requests",
        labels={
            "complexity_tier": "Complexity Tier",
            "requests": "Requests"
        }
    )

    fig.update_layout(
        dragmode=False,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "scrollZoom": False,
            "displayModeBar": False
        }
    )


st.dataframe(
    tier_summary,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# COST BASELINE COMPARISON
# ============================================================

st.header("Cost Baseline Comparison")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Dynamic Routing",
        f"${total_cost:.6f}"
    )

with col2:
    st.metric(
        "All-Sonnet Baseline",
        f"${all_sonnet_cost:.6f}"
    )

with col3:
    st.metric(
        "Estimated Savings",
        f"${estimated_savings:.6f}"
    )


baseline_data = pd.DataFrame(
    {
        "Strategy": [
            "Dynamic Routing",
            "All-Sonnet"
        ],
        "Cost": [
            total_cost,
            all_sonnet_cost
        ]
    }
)

fig = px.bar(
    baseline_data,
    x="Strategy",
    y="Cost",
    labels={
        "Strategy": "Strategy",
        "Cost": "Cost (USD)"
    }
)

fig.update_layout(
    dragmode=False,
    margin=dict(l=20, r=20, t=20, b=20)
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "scrollZoom": False,
        "displayModeBar": False
    }
)


# ============================================================
# FEEDBACK / QUALITY / ESCALATION
# ============================================================

st.header("Feedback, Quality & Escalation")

positive_feedback = (
    (df["feedback"] == "positive").sum()
)

negative_feedback = (
    (df["feedback"] == "negative").sum()
)

quality_failures = (
    (df["quality_passed"] == 0).sum()
)

total_escalations = (
    (df["escalated"] == 1).sum()
)

escalation_cost = (
    df["additional_cost"].fillna(0).sum()
)


col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Positive Feedback",
        positive_feedback
    )

with col2:
    st.metric(
        "Negative Feedback",
        negative_feedback
    )

with col3:
    st.metric(
        "Quality Failures",
        quality_failures
    )

with col4:
    st.metric(
        "Escalations",
        total_escalations
    )

with col5:
    st.metric(
        "Escalation Cost",
        f"${escalation_cost:.6f}"
    )


# ============================================================
# REQUEST DETAILS
# ============================================================

st.header("Request Details")

display_columns = [
    "id",
    "complexity_tier",
    "classifier_confidence",
    "model_name",
    "provider",
    "input_tokens",
    "output_tokens",
    "latency_ms",
    "cost",
    "feedback",
    "quality_score",
    "escalated"
]

st.dataframe(
    df[display_columns],
    use_container_width=True,
    hide_index=True
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "LLM Cost Autopilot | Dynamic model routing, "
    "cost optimization, quality verification and escalation"
)