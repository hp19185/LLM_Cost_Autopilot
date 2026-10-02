from app.database import get_connection


connection = get_connection()

cursor = connection.cursor()


cursor.execute(
    """
    SELECT
        id,
        timestamp,
        complexity_tier,
        model_name,
        input_tokens,
        output_tokens,
        latency_ms,
        cost,
        escalated

    FROM requests

    ORDER BY id
    """
)


rows = cursor.fetchall()


print("\n========================================")
print("         REQUEST LOGS")
print("========================================")


for row in rows:

    print("\n----------------------------------------")

    print(
        "Request ID:",
        row["id"]
    )

    print(
        "Timestamp:",
        row["timestamp"]
    )

    print(
        "Complexity Tier:",
        row["complexity_tier"]
    )

    print(
        "Model:",
        row["model_name"]
    )

    print(
        "Input Tokens:",
        row["input_tokens"]
    )

    print(
        "Output Tokens:",
        row["output_tokens"]
    )

    print(
        "Latency:",
        round(row["latency_ms"], 2),
        "ms"
    )

    print(
        "Cost: $",
        row["cost"]
    )

    print(
        "Escalated:",
        bool(row["escalated"])
    )


connection.close()