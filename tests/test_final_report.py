import sqlite3
from pathlib import Path

import pandas as pd


# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "autopilot.db"

SONNET_INPUT_COST_PER_MILLION = 3.0
SONNET_OUTPUT_COST_PER_MILLION = 15.0


# ============================================================
# Database
# ============================================================

def load_requests():
    connection = sqlite3.connect(DB_PATH)

    query = """
        SELECT
            id,
            complexity_tier,
            classifier_confidence,
            model_name,
            provider,
            input_tokens,
            output_tokens,
            latency_ms,
            cost,
            quality_score,
            escalated,
            escalated_model,
            feedback,
            quality_passed,
            additional_cost
        FROM requests
        ORDER BY id
    """

    dataframe = pd.read_sql_query(query, connection)

    connection.close()

    return dataframe


# ============================================================
# Sonnet Baseline
# ============================================================

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


# ============================================================
# Main Report
# ============================================================

def main():

    df = load_requests()

    if df.empty:
        print("No request records found.")
        return

    # --------------------------------------------------------
    # Overall Cost
    # --------------------------------------------------------

    total_requests = len(df)

    dynamic_routing_cost = (
        df["cost"].fillna(0).sum()
    )

    average_cost = (
        df["cost"].fillna(0).mean()
    )

    df["sonnet_baseline_cost"] = df.apply(
        calculate_sonnet_cost,
        axis=1
    )

    all_sonnet_cost = (
        df["sonnet_baseline_cost"].sum()
    )

    estimated_savings = (
        all_sonnet_cost - dynamic_routing_cost
    )

    cost_reduction = (
        estimated_savings / all_sonnet_cost * 100
        if all_sonnet_cost > 0
        else 0
    )

    # --------------------------------------------------------
    # Feedback / Quality / Escalation
    # --------------------------------------------------------

    positive_feedback = (
        df["feedback"] == "positive"
    ).sum()

    negative_feedback = (
        df["feedback"] == "negative"
    ).sum()

    quality_failures = (
        df["quality_passed"] == 0
    ).sum()

    total_escalations = (
        df["escalated"] == 1
    ).sum()

    escalation_cost = (
        df["additional_cost"]
        .fillna(0)
        .sum()
    )

    # --------------------------------------------------------
    # Print Report
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("              LLM COST AUTOPILOT")
    print("              FINAL EXPERIMENT REPORT")
    print("=" * 70)

    print()
    print("OVERALL RESULTS")
    print("-" * 70)

    print(f"Total Requests          : {total_requests}")
    print(f"Dynamic Routing Cost    : ${dynamic_routing_cost:.6f}")
    print(f"Average Cost / Request  : ${average_cost:.6f}")
    print(f"All-Sonnet Cost         : ${all_sonnet_cost:.6f}")
    print(f"Estimated Savings       : ${estimated_savings:.6f}")
    print(f"Cost Reduction          : {cost_reduction:.2f}%")

    # --------------------------------------------------------
    # Model Distribution
    # --------------------------------------------------------

    print()
    print("MODEL DISTRIBUTION")
    print("-" * 70)

    model_summary = (
        df.groupby("model_name")
        .agg(
            requests=("id", "count"),
            total_cost=("cost", "sum"),
            average_cost=("cost", "mean"),
            average_latency_ms=("latency_ms", "mean")
        )
        .reset_index()
    )

    for _, row in model_summary.iterrows():

        print(
            f"{row['model_name']:20}"
            f" Requests: {int(row['requests']):2d}"
            f" | Cost: ${row['total_cost']:.6f}"
            f" | Avg Cost: ${row['average_cost']:.6f}"
            f" | Avg Latency: {row['average_latency_ms']:.2f} ms"
        )

    # --------------------------------------------------------
    # Complexity Tier Distribution
    # --------------------------------------------------------

    print()
    print("COMPLEXITY TIER DISTRIBUTION")
    print("-" * 70)

    tier_summary = (
        df.groupby("complexity_tier")
        .agg(
            requests=("id", "count"),
            total_cost=("cost", "sum"),
            average_confidence=("classifier_confidence", "mean")
        )
        .reset_index()
    )

    for _, row in tier_summary.iterrows():

        print(
            f"Tier {int(row['complexity_tier'])}"
            f" | Requests: {int(row['requests']):2d}"
            f" | Cost: ${row['total_cost']:.6f}"
            f" | Avg Confidence: "
            f"{row['average_confidence'] * 100:.2f}%"
        )

    # --------------------------------------------------------
    # Quality and Escalation
    # --------------------------------------------------------

    print()
    print("QUALITY AND ESCALATION")
    print("-" * 70)

    print(f"Positive Feedback      : {positive_feedback}")
    print(f"Negative Feedback      : {negative_feedback}")
    print(f"Quality Failures       : {quality_failures}")
    print(f"Total Escalations      : {total_escalations}")
    print(f"Escalation Cost        : ${escalation_cost:.6f}")

    # --------------------------------------------------------
    # Routing Efficiency
    # --------------------------------------------------------

    print()
    print("ROUTING EFFICIENCY")
    print("-" * 70)

    for _, row in tier_summary.iterrows():

        request_share = (
            row["requests"] / total_requests * 100
        )

        cost_share = (
            row["total_cost"]
            / dynamic_routing_cost
            * 100
            if dynamic_routing_cost > 0
            else 0
        )

        print(
            f"Tier {int(row['complexity_tier'])}"
            f" | Request Share: {request_share:.2f}%"
            f" | Cost Share: {cost_share:.2f}%"
        )

    print()
    print("=" * 70)
    print("REPORT COMPLETE")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()