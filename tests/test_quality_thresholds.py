from app.quality_thresholds import (
    QUALITY_THRESHOLDS,
    get_quality_threshold
)


print("\n========================================")
print("       QUALITY THRESHOLD TEST")
print("========================================")


# ============================================================
# Display all configured thresholds
# ============================================================

print("\n----- AVAILABLE QUALITY RULES -----")

for task_type, threshold in QUALITY_THRESHOLDS.items():

    print("\nTask Type:", task_type)

    print(
        "Minimum Score:",
        threshold.minimum_score
    )

    print(
        "Use LLM Judge:",
        threshold.use_llm_judge
    )

    print(
        "Deterministic Check:",
        threshold.deterministic_check
    )


# ============================================================
# Test individual lookup
# ============================================================

print("\n----- LOOKUP TEST -----")

task_type = "summarization"

threshold = get_quality_threshold(
    task_type
)

print(
    "Task:",
    task_type
)

print(
    "Minimum acceptable score:",
    threshold.minimum_score
)

print(
    "LLM judge required:",
    threshold.use_llm_judge
)

print(
    "Deterministic check:",
    threshold.deterministic_check
)