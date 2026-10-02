from app.database import get_connection


def reset_request_data():
    connection = get_connection()
    cursor = connection.cursor()

    # Show current number of records
    cursor.execute("SELECT COUNT(*) AS total FROM requests")
    total = cursor.fetchone()["total"]

    print("\n" + "=" * 60)
    print("DATABASE RESET")
    print("=" * 60)
    print(f"Current request records: {total}")

    if total == 0:
        print("Database is already empty.")
        connection.close()
        return

    confirmation = input(
        "\nDelete all request records? (y/n): "
    ).strip().lower()

    if confirmation != "y":
        print("\nReset cancelled.")
        connection.close()
        return

    cursor.execute("DELETE FROM requests")

    connection.commit()

    print("\nAll request records have been deleted.")
    print("Database structure has been preserved.")

    connection.close()


if __name__ == "__main__":
    reset_request_data()