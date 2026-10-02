import sqlite3
from pathlib import Path
from datetime import datetime


# ============================================================
# Database location
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_DIR = BASE_DIR / "data"

DB_DIR.mkdir(
    exist_ok=True
)

DB_PATH = DB_DIR / "autopilot.db"


# ============================================================
# Database connection
# ============================================================

def get_connection():

    connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# Create / update database table
# ============================================================

def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    # --------------------------------------------------------
    # Create requests table if it does not exist
    # --------------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS requests (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            timestamp TEXT NOT NULL,

            prompt_hash TEXT NOT NULL,

            complexity_tier INTEGER,

            classifier_confidence REAL,

            model_name TEXT,

            provider TEXT,

            model_id TEXT,

            input_tokens INTEGER,

            output_tokens INTEGER,

            latency_ms REAL,

            cost REAL,

            quality_score REAL,

            escalated INTEGER DEFAULT 0,

            escalated_model TEXT,

            feedback TEXT,

            quality_passed INTEGER,

            verification_method TEXT,

            user_consent INTEGER,

            original_cost REAL,

            escalated_cost REAL,

            additional_cost REAL,

            total_cost REAL

        )
        """
    )

    # --------------------------------------------------------
    # Add missing columns to an existing database
    # --------------------------------------------------------

    cursor.execute(
        "PRAGMA table_info(requests)"
    )

    columns = [
        row["name"]
        for row in cursor.fetchall()
    ]

    required_columns = {

        "feedback":
            "TEXT",

        "quality_passed":
            "INTEGER",

        "verification_method":
            "TEXT",

        "user_consent":
            "INTEGER",

        "original_cost":
            "REAL",

        "escalated_cost":
            "REAL",

        "additional_cost":
            "REAL",

        "total_cost":
            "REAL"
    }

    for column_name, column_type in required_columns.items():

        if column_name not in columns:
            cursor.execute(
                f"""
                ALTER TABLE requests
                ADD COLUMN {column_name} {column_type}
                """
            )

    connection.commit()

    connection.close()


# ============================================================
# Insert request record
# ============================================================

def log_request(

    prompt_hash,

    complexity_tier,

    classifier_confidence,

    model_name,

    provider,

    model_id,

    input_tokens,

    output_tokens,

    latency_ms,

    cost,

    quality_score=None,

    escalated=False,

    escalated_model=None

):

    connection = get_connection()

    cursor = connection.cursor()

    timestamp = datetime.now().isoformat()

    cursor.execute(
        """
        INSERT INTO requests (

            timestamp,
            prompt_hash,
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
            escalated_model

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,

        (
            timestamp,
            prompt_hash,
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
            int(escalated),
            escalated_model
        )
    )

    connection.commit()

    request_id = cursor.lastrowid

    connection.close()

    return request_id


# ============================================================
# Record user feedback
# ============================================================

def record_feedback(
    request_id,
    feedback
):

    feedback = feedback.lower().strip()

    if feedback not in [
        "positive",
        "negative"
    ]:

        raise ValueError(
            "Feedback must be 'positive' or 'negative'."
        )

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE requests

        SET feedback = ?

        WHERE id = ?
        """,

        (
            feedback,
            request_id
        )
    )

    if cursor.rowcount == 0:

        connection.close()

        raise ValueError(
            f"Request ID {request_id} not found."
        )

    connection.commit()

    connection.close()


# ============================================================
# Get feedback for a request
# ============================================================

def get_feedback(request_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT feedback

        FROM requests

        WHERE id = ?
        """,

        (
            request_id,
        )
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:

        raise ValueError(
            f"Request ID {request_id} not found."
        )

    return row["feedback"]


def update_quality_result(
    request_id,
    quality_score,
    quality_passed,
    verification_method
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE requests
        SET
            quality_score = ?,
            quality_passed = ?,
            verification_method = ?
        WHERE id = ?
    """, (
        quality_score,
        1 if quality_passed else 0,
        verification_method,
        request_id
    ))

    if cursor.rowcount == 0:
        connection.close()
        raise ValueError(f"Request ID {request_id} not found.")

    connection.commit()
    connection.close()


def update_escalation_result(
    request_id,
    user_consent,
    escalated,
    escalated_model=None,
    original_cost=None,
    escalated_cost=None,
    additional_cost=None,
    total_cost=None
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE requests
        SET
            user_consent = ?,
            escalated = ?,
            escalated_model = ?,
            original_cost = ?,
            escalated_cost = ?,
            additional_cost = ?,
            total_cost = ?
        WHERE id = ?
    """, (
        1 if user_consent else 0,
        1 if escalated else 0,
        escalated_model,
        original_cost,
        escalated_cost,
        additional_cost,
        total_cost,
        request_id
    ))

    if cursor.rowcount == 0:
        connection.close()
        raise ValueError(f"Request ID {request_id} not found.")

    connection.commit()
    connection.close()