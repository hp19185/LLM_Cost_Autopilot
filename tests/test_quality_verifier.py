from app.quality_verifier import QualityVerifier


print("\n========================================")
print("        QUALITY VERIFIER TEST")
print("========================================")


verifier = QualityVerifier()


# ============================================================
# TEST 1 — JSON
# ============================================================

print("\n----------------------------------------")
print("TEST #1 — JSON VALIDATION")
print("----------------------------------------")

json_response = """
{
    "name": "John",
    "age": 30
}
"""

result = verifier.verify(
    task_type="json",
    original_prompt="Convert the information into JSON.",
    response=json_response
)

print("Method:", result["method"])
print("Passed:", result["passed"])
print("Score:", result["score"])
print("Reason:", result["reason"])


# ============================================================
# TEST 2 — Classification
# ============================================================

print("\n----------------------------------------")
print("TEST #2 — CLASSIFICATION")
print("----------------------------------------")

classification_response = "Positive"

result = verifier.verify(
    task_type="classification",
    original_prompt="Classify the customer feedback.",
    response=classification_response,
    expected_output="Positive"
)

print("Method:", result["method"])
print("Passed:", result["passed"])
print("Score:", result["score"])
print("Reason:", result["reason"])


# ============================================================
# TEST 3 — Extraction
# ============================================================

print("\n----------------------------------------")
print("TEST #3 — EXTRACTION")
print("----------------------------------------")

extraction_response = """
John's email is john@gmail.com.
Alice's email is alice@gmail.com.
"""

result = verifier.verify(
    task_type="extraction",
    original_prompt="Extract all email addresses.",
    response=extraction_response,
    expected_output=[
        "john@gmail.com",
        "alice@gmail.com"
    ]
)

print("Method:", result["method"])
print("Passed:", result["passed"])
print("Score:", result["score"])
print("Reason:", result["reason"])


# ============================================================
# TEST 4 — Summarization
# ============================================================

print("\n----------------------------------------")
print("TEST #4 — SUMMARIZATION")
print("----------------------------------------")

summary_response = """
Machine learning allows computers to learn patterns
from data and make predictions without being explicitly
programmed for every individual task.
"""

result = verifier.verify(
    task_type="summarization",
    original_prompt=(
        "Summarize the concept of machine learning "
        "in a few sentences."
    ),
    response=summary_response
)

print("Method:", result["method"])
print("Passed:", result["passed"])
print("Score:", result["score"])
print("Reason:", result["reason"])

print(
    "\nJudge Model:",
    result["judge_model"]
)

print(
    "Judge Cost: $",
    result["judge_cost"]
)

print(
    "Judge Latency:",
    round(
        result["judge_latency_ms"],
        2
    ),
    "ms"
)