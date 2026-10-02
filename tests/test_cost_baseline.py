from app.database import get_connection


# ============================================================
# SONNET PRICING
# ============================================================

SONNET_INPUT_COST_PER_MILLION = 3.0
SONNET_OUTPUT_COST_PER_MILLION = 15.0


# ============================================================
# Calculate hypothetical Sonnet cost
# ============================================================

def calculate_sonnet_cost(input_tokens, output_tokens):

    input_cost = (
        input_tokens / 1_000_000
    ) * SONNET_INPUT_COST_PER_MILLION

    output_cost = (
        output_tokens / 1_000_000
    ) * SONNET_OUTPUT_COST_PER_MILLION

    return input_cost + output_cost


# ============================================================
# Main baseline analysis
# ============================================================

def run_baseline_analysis():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            model_name,
            complexity_tier,
            input_tokens,
            output_tokens,
            cost
        FROM requests
        ORDER BY id
        """
    )

    records = cursor.fetchall()

    connection.close()

    if not records:

        print("No request records found.")

        return

    # --------------------------------------------------------
    # Actual dynamic-routing cost
    # --------------------------------------------------------

    actual_cost = sum(
        row["cost"] or 0
        for row in records
    )

    # --------------------------------------------------------
    # Hypothetical all-Sonnet cost
    # --------------------------------------------------------

    all_sonnet_cost = 0.0

    print("\n============================================================")
    print("       LLM COST AUTOPILOT - COST BASELINE ANALYSIS")
    print("============================================================")

    print(
        f"\nTotal Requests : {len(records)}"
    )

    print("\n----- REQUEST-WISE BASELINE -----")

    for row in records:

        sonnet_cost = calculate_sonnet_cost(
            row["input_tokens"] or 0,
            row["output_tokens"] or 0
        )

        all_sonnet_cost += sonnet_cost

        print("\nRequest ID       :", row["id"])
        print("Model            :", row["model_name"])
        print("Complexity Tier  :", row["complexity_tier"])
        print("Input Tokens     :", row["input_tokens"])
        print("Output Tokens    :", row["output_tokens"])
        print(
            "Actual Cost      : $ {:.6f}".format(
                row["cost"] or 0
            )
        )
        print(
            "Sonnet Cost      : $ {:.6f}".format(
                sonnet_cost
            )
        )

    # --------------------------------------------------------
    # Savings calculation
    # --------------------------------------------------------

    savings = (
        all_sonnet_cost - actual_cost
    )

    if all_sonnet_cost > 0:

        savings_percentage = (
            savings / all_sonnet_cost
        ) * 100

    else:

        savings_percentage = 0.0

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    print("\n============================================================")
    print("                 FINAL COST COMPARISON")
    print("============================================================")

    print(
        "Dynamic Routing Cost : $ {:.6f}".format(
            actual_cost
        )
    )

    print(
        "All-Sonnet Cost      : $ {:.6f}".format(
            all_sonnet_cost
        )
    )

    print(
        "Estimated Savings    : $ {:.6f}".format(
            savings
        )
    )

    print(
        "Cost Reduction       : {:.2f}%".format(
            savings_percentage
        )
    )

    print("============================================================")


if __name__ == "__main__":

    run_baseline_analysis()