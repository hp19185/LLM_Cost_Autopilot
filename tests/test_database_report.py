from app.database import get_connection


def show_database_report():
    connection = get_connection()
    cursor = connection.cursor()

    print("\n" + "=" * 60)
    print("       LLM COST AUTOPILOT - DATABASE REPORT")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Total requests
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT COUNT(*) AS total_requests
        FROM requests
    """)

    total_requests = cursor.fetchone()["total_requests"]

    # ---------------------------------------------------------
    # 2. Total cost
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT COALESCE(SUM(cost), 0) AS total_cost
        FROM requests
    """)

    total_cost = cursor.fetchone()["total_cost"]

    # ---------------------------------------------------------
    # 3. Average cost
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT COALESCE(AVG(cost), 0) AS average_cost
        FROM requests
    """)

    average_cost = cursor.fetchone()["average_cost"]

    # ---------------------------------------------------------
    # 4. Positive feedback
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT COUNT(*) AS positive_feedback
        FROM requests
        WHERE feedback = 'positive'
    """)

    positive_feedback = cursor.fetchone()["positive_feedback"]

    # ---------------------------------------------------------
    # 5. Negative feedback
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT COUNT(*) AS negative_feedback
        FROM requests
        WHERE feedback = 'negative'
    """)

    negative_feedback = cursor.fetchone()["negative_feedback"]

    # ---------------------------------------------------------
    # 6. Quality failures
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT COUNT(*) AS quality_failures
        FROM requests
        WHERE quality_passed = 0
    """)

    quality_failures = cursor.fetchone()["quality_failures"]

    # ---------------------------------------------------------
    # 7. Total escalations
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT COUNT(*) AS total_escalations
        FROM requests
        WHERE escalated = 1
    """)

    total_escalations = cursor.fetchone()["total_escalations"]

    # ---------------------------------------------------------
    # 8. Total escalation cost
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT COALESCE(SUM(additional_cost), 0) AS escalation_cost
        FROM requests
        WHERE escalated = 1
    """)

    escalation_cost = cursor.fetchone()["escalation_cost"]

    # ---------------------------------------------------------
    # Display report
    # ---------------------------------------------------------

    print(f"\nTotal Requests       : {total_requests}")
    print(f"Total Cost           : $ {total_cost:.6f}")
    print(f"Average Cost         : $ {average_cost:.6f}")

    print("\n----- USER FEEDBACK -----")
    print(f"Positive Feedback    : {positive_feedback}")
    print(f"Negative Feedback    : {negative_feedback}")

    print("\n----- QUALITY -----")
    print(f"Quality Failures     : {quality_failures}")

    print("\n----- ESCALATION -----")
    print(f"Total Escalations    : {total_escalations}")
    print(f"Escalation Cost      : $ {escalation_cost:.6f}")

    print("\n" + "=" * 60)

    # ---------------------------------------------------------
    # 9. Model-wise analysis
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT
            model_name,
            COUNT(*) AS request_count,
            COALESCE(SUM(cost), 0) AS total_cost,
            COALESCE(AVG(cost), 0) AS average_cost
        FROM requests
        GROUP BY model_name
        ORDER BY total_cost DESC
    """)

    model_rows = cursor.fetchall()

    print("\n----- MODEL-WISE ANALYSIS -----")

    for row in model_rows:
        print(f"Model: {row['model_name']}")
        print(f"  Requests     : {row['request_count']}")
        print(f"  Total Cost   : $ {row['total_cost']:.6f}")
        print(f"  Average Cost : $ {row['average_cost']:.6f}")
        print()

    # ---------------------------------------------------------
    # 10. Complexity-tier analysis
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT
            complexity_tier,
            COUNT(*) AS request_count,
            COALESCE(SUM(cost), 0) AS total_cost,
            COALESCE(AVG(cost), 0) AS average_cost
        FROM requests
        GROUP BY complexity_tier
        ORDER BY complexity_tier
    """)

    tier_rows = cursor.fetchall()

    print("\n----- COMPLEXITY-TIER ANALYSIS -----")

    for row in tier_rows:
        print(f"Tier: {row['complexity_tier']}")
        print(f"  Requests     : {row['request_count']}")
        print(f"  Total Cost   : $ {row['total_cost']:.6f}")
        print(f"  Average Cost : $ {row['average_cost']:.6f}")
        print()

    # ---------------------------------------------------------
    # 11. Routing efficiency
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT
            complexity_tier,
            COUNT(*) AS request_count,
            COALESCE(SUM(cost), 0) AS total_cost
        FROM requests
        GROUP BY complexity_tier
        ORDER BY complexity_tier
    """)

    efficiency_rows = cursor.fetchall()

    print("\n----- ROUTING EFFICIENCY -----")

    for row in efficiency_rows:
        request_percentage = (
            row["request_count"] / total_requests * 100
            if total_requests > 0 else 0
        )

        cost_percentage = (
            row["total_cost"] / total_cost * 100
            if total_cost > 0 else 0
        )

        print(f"Tier: {row['complexity_tier']}")
        print(f"  Request Share : {request_percentage:.2f}%")
        print(f"  Cost Share    : {cost_percentage:.2f}%")
        print()
    connection.close()


if __name__ == "__main__":
    show_database_report()