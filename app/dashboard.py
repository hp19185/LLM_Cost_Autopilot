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
            task_type,
            task_type_confidence,
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

# -----------------------------
# Dashboard Filters
# -----------------------------

st.sidebar.header("Filters")

# Model filter
model_options = ["All"] + sorted(df["model_name"].dropna().unique().tolist())
selected_model = st.sidebar.selectbox(
    "Model",
    model_options
)

# Complexity tier filter
tier_options = ["All"] + sorted(df["complexity_tier"].dropna().unique().tolist())
selected_tier = st.sidebar.selectbox(
    "Complexity Tier",
    tier_options
)

# Provider filter
provider_options = ["All"] + sorted(df["provider"].dropna().unique().tolist())
selected_provider = st.sidebar.selectbox(
    "Provider",
    provider_options
)

# Apply filters
filtered_df = df.copy()

if selected_model != "All":
    filtered_df = filtered_df[
        filtered_df["model_name"] == selected_model
    ]

if selected_tier != "All":
    filtered_df = filtered_df[
        filtered_df["complexity_tier"] == selected_tier
    ]

if selected_provider != "All":
    filtered_df = filtered_df[
        filtered_df["provider"] == selected_provider
    ]
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

total_requests = len(filtered_df)
total_cost = filtered_df["cost"].fillna(0).sum()
average_cost = (
    filtered_df["cost"].fillna(0).mean()
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


filtered_df["sonnet_baseline_cost"] = filtered_df.apply(
    calculate_sonnet_cost,
    axis=1
)

all_sonnet_cost = filtered_df["sonnet_baseline_cost"].sum()

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
    filtered_df.groupby("model_name")
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
    filtered_df.groupby("complexity_tier")
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

# -----------------------------
# Latency Analysis
# -----------------------------

st.subheader("Latency Analysis")

latency_summary = (
    filtered_df.groupby("model_name")
    .agg(
        average_latency_ms=("latency_ms", "mean"),
        minimum_latency_ms=("latency_ms", "min"),
        maximum_latency_ms=("latency_ms", "max")
    )
    .reset_index()
)

st.dataframe(
    latency_summary,
    use_container_width=True
)

fig_latency = px.bar(
    latency_summary,
    x="model_name",
    y="average_latency_ms",
    title="Average Latency by Model",
    labels={
        "model_name": "Model",
        "average_latency_ms": "Average Latency (ms)"
    },
    text_auto=".0f"
)

fig_latency.update_layout(
    dragmode=False,
    margin=dict(l=20, r=20, t=40, b=20)
)

st.plotly_chart(
    fig_latency,
    use_container_width=True,
    config={
        "scrollZoom": False,
        "displayModeBar": False
    }
)

# -----------------------------
# Classifier Confidence Analysis
# -----------------------------

st.subheader("Classifier Confidence Analysis")

confidence_summary = (
    filtered_df.groupby("complexity_tier")
    .agg(
        average_confidence=("classifier_confidence", "mean"),
        minimum_confidence=("classifier_confidence", "min"),
        maximum_confidence=("classifier_confidence", "max")
    )
    .reset_index()
)

confidence_summary["average_confidence"] = (
    confidence_summary["average_confidence"] * 100
)

confidence_summary["minimum_confidence"] = (
    confidence_summary["minimum_confidence"] * 100
)

confidence_summary["maximum_confidence"] = (
    confidence_summary["maximum_confidence"] * 100
)

st.dataframe(
    confidence_summary,
    use_container_width=True
)

fig_confidence = px.bar(
    confidence_summary,
    x="complexity_tier",
    y="average_confidence",
    title="Average Classifier Confidence by Complexity Tier",
    labels={
        "complexity_tier": "Complexity Tier",
        "average_confidence": "Average Confidence (%)"
    },
    text_auto=".1f"
)

fig_confidence.update_layout(
    dragmode=False,
    margin=dict(l=20, r=20, t=40, b=20)
)

st.plotly_chart(
    fig_confidence,
    use_container_width=True,
    config={
        "scrollZoom": False,
        "displayModeBar": False
    }
)

# -----------------------------
# Quality & Escalation Monitoring
# -----------------------------

st.subheader("Quality & Escalation Monitoring")

positive_feedback = (
    filtered_df["feedback"] == "positive"
).sum()

negative_feedback = (
    filtered_df["feedback"] == "negative"
).sum()

quality_failures = (
    filtered_df["quality_passed"] == 0
).sum()

total_escalations = (
    filtered_df["escalated"] == 1
).sum()

escalation_cost = (
    filtered_df["additional_cost"]
    .fillna(0)
    .sum()
)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Positive Feedback",
    positive_feedback
)

col2.metric(
    "Negative Feedback",
    negative_feedback
)

col3.metric(
    "Quality Failures",
    quality_failures
)

col4.metric(
    "Escalations",
    total_escalations
)

col5.metric(
    "Escalation Cost",
    f"${escalation_cost:.6f}"
)

feedback_data = pd.DataFrame(
    {
        "Feedback": [
            "Positive",
            "Negative"
        ],
        "Count": [
            positive_feedback,
            negative_feedback
        ]
    }
)

fig_feedback = px.bar(
    feedback_data,
    x="Feedback",
    y="Count",
    title="User Feedback",
    text_auto=True
)

fig_feedback.update_layout(
    dragmode=False,
    margin=dict(l=20, r=20, t=40, b=20)
)

st.plotly_chart(
    fig_feedback,
    use_container_width=True,
    config={
        "scrollZoom": False,
        "displayModeBar": False
    }
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
    (filtered_df["feedback"] == "positive").sum()
)

negative_feedback = (
    (filtered_df["feedback"] == "negative").sum()
)

quality_failures = (
    (filtered_df["quality_passed"] == 0).sum()
)

total_escalations = (
    (filtered_df["escalated"] == 1).sum()
)

escalation_cost = (
    filtered_df["additional_cost"].fillna(0).sum()
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
    "task_type",
    "task_type_confidence",
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
    filtered_df[display_columns],
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