from app.autopilot import LLMCostAutopilot


print("\n========================================")
print("   REAL ESCALATION CONSENT TEST")
print("========================================")


autopilot = LLMCostAutopilot()


# ============================================================
# 1. Create the real request
# ============================================================

prompt = "What is OOP?"

task_type = "basic_qa"


print("\n----- USER REQUEST -----")
print(prompt)


result = autopilot.process_request(
    prompt=prompt,
    task_type=task_type
)


print("\n----- INITIAL RESPONSE -----")

print(result["output"])


print("\n----- RESPONSE INFORMATION -----")

print(
    "Request ID:",
    result["request_id"]
)

print(
    "Original Model:",
    result["model"]
)

print(
    "Provider:",
    result["provider"]
)

print(
    "Cost: $",
    result["cost"]
)

print(
    "Latency:",
    round(
        result["latency_ms"],
        2
    ),
    "ms"
)


# ============================================================
# 2. Simulate negative feedback
# ============================================================

print(
    "\n----------------------------------------"
)

print(
    "Simulating negative user feedback..."
)


# ============================================================
# 3. Perform normal feedback processing
# ============================================================

feedback_result = autopilot.submit_feedback(
    request_id=result["request_id"],
    feedback="negative"
)


print(
    "\n----- FEEDBACK RESULT -----"
)


print(
    "Quality Score:",
    feedback_result.get(
        "quality_score"
    )
)

print(
    "Quality Passed:",
    feedback_result.get(
        "quality_passed"
    )
)

print(
    "Current Model:",
    feedback_result.get(
        "current_model"
    )
)

print(
    "Next Model:",
    feedback_result.get(
        "next_model"
    )
)

print(
    "Escalation Available:",
    feedback_result.get(
        "escalation_available"
    )
)


# ============================================================
# 4. Normal quality verification may pass
# ============================================================
#
# For this controlled test we need to force the verification
# result to represent a quality failure.
#
# We do NOT modify the real QualityVerifier.
#

if feedback_result.get(
    "quality_passed"
) is True:

    print(
        "\nThe real verifier accepted "
        "the response."
    )

    print(
        "For this controlled test, we will "
        "simulate a quality failure."
    )

    current_model_name = result[
        "model"
    ]

    next_model = (
        autopilot.escalation_manager
        .get_next_model(
            current_model_name
        )
    )

    if next_model is None:

        print(
            "\nNo higher-tier model available."
        )

        raise SystemExit


    next_model_name = (
        autopilot._get_model_name(
            next_model
        )
    )

    escalation_available = True

else:

    current_model_name = (
        feedback_result[
            "current_model"
        ]
    )

    next_model_name = (
        feedback_result[
            "next_model"
        ]
    )

    escalation_available = (
        feedback_result.get(
            "escalation_available"
        )
        is True
    )


# ============================================================
# 5. Ask for user consent
# ============================================================

if escalation_available:

    print(
        "\n----------------------------------------"
    )

    print(
        "Quality verification has identified "
        "a quality failure."
    )

    print(
        "Current Model:",
        current_model_name
    )

    print(
        "Higher Model:",
        next_model_name
    )

    print(
        "\nThe higher-tier model may increase "
        "cost and latency."
    )

    consent = input(
        "\nDo you want to use the "
        "higher-tier model? (y/n): "
    )


    # ========================================================
    # 6. User gives consent
    # ========================================================

    if consent.lower().strip() == "y":

        print(
            "\nUser consent received."
        )

        print(
            "Calling approve_escalation()..."
        )


        escalation_result = (
            autopilot.approve_escalation(
                request_id=result[
                    "request_id"
                ]
            )
        )


        # ====================================================
        # 7. Display actual escalated response
        # ====================================================

        print(
            "\n----- ESCALATED RESPONSE -----"
        )

        print(
            escalation_result[
                "output"
            ]
        )


        print(
            "\n----- ESCALATION RESULT -----"
        )

        print(
            "Original Model:",
            escalation_result[
                "original_model"
            ]
        )

        print(
            "Escalated Model:",
            escalation_result[
                "escalated_model"
            ]
        )

        print(
            "Additional Cost: $",
            escalation_result[
                "additional_cost"
            ]
        )

        print(
            "Total Cost: $",
            escalation_result[
                "total_cost"
            ]
        )

        print(
            "Escalated:",
            escalation_result[
                "escalated"
            ]
        )

    # ========================================================
    # 8. User declines consent
    # ========================================================

    else:

        print(
            "\nUser declined escalation."
        )

        print(
            "Original response will be kept."
        )


else:

    print(
        "\nNo escalation available."
    )

    print(
        "Original response will be kept."
    )