from app.autopilot import LLMCostAutopilot


print("\n========================================")
print("       ESCALATION CONSENT TEST")
print("========================================")


autopilot = LLMCostAutopilot()


# ============================================================
# TEST OVERRIDE: Force quality failure
# ============================================================

class ForcedFailureVerifier:

    def verify(
        self,
        task_type,
        original_prompt,
        response
    ):

        return {
            "method": "test_forced_failure",
            "score": 2.0,
            "passed": False,
            "reason": "Forced quality failure for escalation testing."
        }


autopilot.verifier = ForcedFailureVerifier()


# ============================================================
# 1. Generate a normal request
# ============================================================

prompt = "What is Python?"

task_type = "basic_qa"


print("\n----- USER REQUEST -----")
print(prompt)


result = autopilot.process_request(
    prompt=prompt,
    task_type=task_type
)


# ============================================================
# 2. Display initial response
# ============================================================

print("\n----- INITIAL RESPONSE -----")

print(result["output"])


print("\n----- RESPONSE INFORMATION -----")

print("Request ID:", result["request_id"])
print("Model:", result["model"])
print("Provider:", result["provider"])
print("Cost: $", result["cost"])


# ============================================================
# 3. Simulate negative user feedback
# ============================================================

print("\n----------------------------------------")

print(
    "Simulating negative user feedback..."
)


verification_result = autopilot.submit_feedback(
    request_id=result["request_id"],
    feedback="negative"
)


# ============================================================
# 4. Display quality verification
# ============================================================

print("\n----- QUALITY VERIFICATION -----")

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

print(
    "Escalation Available:",
    verification_result.get(
        "escalation_available"
    )
)


# ============================================================
# 5. Check whether escalation is available
# ============================================================

if verification_result.get(
    "escalation_available"
) is not True:

    print(
        "\nEscalation is not available."
    )

    print(
        "This test cannot continue to "
        "the consent step."
    )

else:

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


    # ========================================================
    # 6. Ask user for consent
    # ========================================================

    consent = input(
        "\nDo you want to use the "
        "higher-tier model? (y/n): "
    )


    # ========================================================
    # 7. User gives consent
    # ========================================================

    if consent.lower().strip() == "y":

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


        # ====================================================
        # 8. Display escalated response
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
            "\n----- ESCALATION INFORMATION -----"
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


    # ========================================================
    # 9. User rejects escalation
    # ========================================================

    else:

        print(
            "\nUser declined escalation."
        )

        print(
            "Original response will be kept."
        )