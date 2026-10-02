from app.autopilot import LLMCostAutopilot
from app.feedback import FeedbackManager


print("\n========================================")
print("       USER FEEDBACK TEST")
print("========================================")


autopilot = LLMCostAutopilot()

feedback_manager = FeedbackManager()


# ============================================================
# 1. User request
# ============================================================

prompt = "What is Python?"

task_type = "basic_qa"


print("\n----- USER REQUEST -----")
print(prompt)


# ============================================================
# 2. Generate initial response
# ============================================================

result = autopilot.process_request(
    prompt=prompt,
    task_type=task_type
)


print("\n----- INITIAL RESPONSE -----")

print(result["output"])


print("\n----- RESPONSE INFORMATION -----")

print("Model:", result["model"])
print("Provider:", result["provider"])
print("Cost: $", result["cost"])

print(
    "Latency:",
    round(result["latency_ms"], 2),
    "ms"
)


# ============================================================
# 3. Ask for user feedback
# ============================================================

print("\n----------------------------------------")

feedback = input(
    "Was this response helpful? (y/n): "
)


# ============================================================
# 4. Process feedback
# ============================================================

feedback_result = feedback_manager.process_feedback(feedback)


# ============================================================
# 5. Invalid feedback
# ============================================================

if not feedback_result["valid"]:

    print(
        "\nInvalid feedback."
    )

    print(
        "Please enter 'y' or 'n'."
    )


# ============================================================
# 6. Positive feedback
# ============================================================

elif feedback_result["feedback"] == "positive":

    print(
        "\nPositive feedback received."
    )

    print(
        "Quality verification is not required."
    )


# ============================================================
# 7. Negative feedback
# ============================================================

elif feedback_result["feedback"] == "negative":

    print(
        "\nNegative feedback received."
    )

    print(
        "Quality verification is required."
    )

    # --------------------------------------------------------
    # Submit negative feedback for quality verification
    # --------------------------------------------------------

    verification_result = autopilot.submit_feedback(
        request_id=result["request_id"],
        feedback="negative"
    )

    print(
        "\n----- QUALITY VERIFICATION -----"
    )

    print(
        "Quality Score:",
        verification_result.get(
            "quality_score"
        )
    )

    print(
        "Quality Passed:",
        verification_result.get(
            "quality_passed"
        )
    )

    print(
        "Current Model:",
        verification_result.get(
            "current_model"
        )
    )

    print(
        "Next Model:",
        verification_result.get(
            "next_model"
        )
    )

    # --------------------------------------------------------
    # Check whether escalation is available
    # --------------------------------------------------------

# ============================================================
# 8. Decide what to do after verification
# ============================================================

    if verification_result.get("quality_passed") is True:

        print(
            "\nQuality verification passed."
        )

        print(
            "The system will NOT escalate "
            "to a higher-cost model."
        )

        print(
            "Original response will be kept."
        )


    elif verification_result.get(
            "escalation_available"
    ) is True:

        print(
            "\nQuality verification failed."
        )

        print(
            "A higher-tier model is available:"
        )

        print(
            verification_result[
                "next_model"
            ]
        )

        print(
            "\nUsing the higher-tier model "
            "may increase cost and latency."
        )

        consent = input(
            "\nDo you want to use the "
            "higher-tier model? (y/n): "
        )

        # --------------------------------------------------------
        # User agrees
        # --------------------------------------------------------

        if consent.lower() == "y":

            print(
                "\nUser consent received."
            )

            print(
                "Escalating request..."
            )

            escalation_result = (
                autopilot.approve_escalation(
                    request_id=result[
                        "request_id"
                    ]
                )
            )

            print(
                "\n----- ESCALATED RESPONSE -----"
            )

            print(
                escalation_result[
                    "output"
                ]
            )

        # --------------------------------------------------------
        # User declines
        # --------------------------------------------------------

        else:

            print(
                "\nUser declined escalation."
            )

            print(
                "Original response will be kept."
            )

    else:

        print(
            "\nQuality verification failed."
        )

        print(
            "No higher-tier model is available."
        )

        print(
            "Original response will be kept."
        )
