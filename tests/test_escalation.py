from app.escalation import EscalationManager


print("\n========================================")
print("          ESCALATION POLICY TEST")
print("========================================")


manager = EscalationManager()


# ============================================================
# Test each model
# ============================================================

models = [
    "llama_local",
    "claude_haiku",
    "claude_sonnet"
]


for model_name in models:

    print("\n----------------------------------------")
    print("Current Model:", model_name)

    can_escalate = manager.can_escalate(
        model_name
    )

    print(
        "Can Escalate:",
        can_escalate
    )

    next_model = manager.get_next_model(
        model_name
    )

    if next_model is None:

        print(
            "Next Model: None"
        )

    else:

        print(
            "Next Model:",
            next_model.model_id
        )

        print(
            "Provider:",
            next_model.provider
        )

        print(
            "Quality Tier:",
            next_model.quality_tier
        )


# ============================================================
# Test cost delta
# ============================================================

print("\n----------------------------------------")
print("COST DELTA TEST")

original_cost = 0.0004
escalated_cost = 0.0020

cost_delta = manager.calculate_cost_delta(
    original_cost,
    escalated_cost
)

print(
    "Original Cost: $",
    original_cost
)

print(
    "Escalated Cost: $",
    escalated_cost
)

print(
    "Additional Cost: $",
    round(cost_delta, 8)
)