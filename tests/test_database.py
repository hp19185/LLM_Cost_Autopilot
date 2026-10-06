from app.database import get_connection


def show_latest_request():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            timestamp,
            model_name,
            provider,
            cost,
            task_type,
            task_type_confidence,
            feedback,
            quality_score,
            quality_passed,
            verification_method,
            user_consent,
            escalated,
            escalated_model,
            original_cost,
            escalated_cost,
            additional_cost,
            total_cost
        FROM requests
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()

    if row is None:
        print("No request records found.")
        connection.close()
        return

    print("\n" + "=" * 60)
    print("LATEST DATABASE RECORD")
    print("=" * 60)

    for key in row.keys():
        print(f"{key:25}: {row[key]}")

    print("=" * 60)

    connection.close()


def show_database_summary():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) AS total_requests,
            COALESCE(SUM(cost), 0) AS total_cost,
            COALESCE(AVG(cost), 0) AS average_cost
        FROM requests
    """)

    summary = cursor.fetchone()

    print("\n" + "=" * 60)
    print("DATABASE SUMMARY")
    print("=" * 60)

    print(f"Total Requests       : {summary['total_requests']}")
    print(f"Total Cost           : ${summary['total_cost']:.6f}")
    print(f"Average Cost         : ${summary['average_cost']:.6f}")

    # ---------------------------------------------------------
    # MODEL-WISE ANALYSIS
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

    print("\n" + "-" * 60)
    print("MODEL-WISE ANALYSIS")
    print("-" * 60)

    for row in model_rows:
        print(f"{row['model_name']:20} : "
              f"{row['request_count']} requests, "
              f"${row['total_cost']:.6f}, "
              f"avg ${row['average_cost']:.6f}")

    # ---------------------------------------------------------
    # TIER-WISE ANALYSIS
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

    print("\n" + "-" * 60)
    print("COMPLEXITY-TIER ANALYSIS")
    print("-" * 60)

    for row in tier_rows:
        print(f"Tier {row['complexity_tier']}               : "
              f"{row['request_count']} requests, "
              f"${row['total_cost']:.6f}, "
              f"avg ${row['average_cost']:.6f}")

    # ---------------------------------------------------------
    # FEEDBACK / QUALITY / ESCALATION
    # ---------------------------------------------------------

    cursor.execute("""
        SELECT
            SUM(CASE WHEN feedback = 'positive' THEN 1 ELSE 0 END)
                AS positive_feedback,

            SUM(CASE WHEN feedback = 'negative' THEN 1 ELSE 0 END)
                AS negative_feedback,

            SUM(CASE WHEN quality_passed = 0 THEN 1 ELSE 0 END)
                AS quality_failures,

            SUM(CASE WHEN escalated = 1 THEN 1 ELSE 0 END)
                AS escalations,

            COALESCE(SUM(additional_cost), 0)
                AS escalation_cost
        FROM requests
    """)

    quality = cursor.fetchone()

    print("\n" + "-" * 60)
    print("FEEDBACK / QUALITY / ESCALATION")
    print("-" * 60)

    print(f"Positive Feedback    : {quality['positive_feedback']}")
    print(f"Negative Feedback    : {quality['negative_feedback']}")
    print(f"Quality Failures     : {quality['quality_failures']}")
    print(f"Total Escalations    : {quality['escalations']}")
    print(f"Escalation Cost      : ${quality['escalation_cost']:.6f}")

    print("=" * 60)

    connection.close()


if __name__ == "__main__":
    show_latest_request()
    show_database_summary()