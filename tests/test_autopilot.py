from app.autopilot import LLMCostAutopilot


print("\n========================================")
print("        LLM COST AUTOPILOT TEST")
print("========================================")


autopilot = LLMCostAutopilot()


# ============================================================
# Test requests
# ============================================================

test_prompts = [

    {
        "prompt": "What is Python?",
        "task_type": "basic_qa"
    },

    {
        "prompt":
        "Summarize the concept of machine learning "
        "in five simple sentences.",
        "task_type": "summarization"
    },

    {
        "prompt":
        "Design a scalable architecture for an "
        "application serving millions of users.",
        "task_type": "architecture"
    }

]


# ============================================================
# Process requests
# ============================================================

for index, test in enumerate(
    test_prompts,
    start=1
):

    prompt = test["prompt"]

    task_type = test["task_type"]

    print("\n----------------------------------------")
    print(f"REQUEST #{index}")
    print("----------------------------------------")

    print("\nPrompt:")
    print(prompt)

    # --------------------------------------------------------
    # Process request
    # --------------------------------------------------------

    result = autopilot.process_request(

        prompt=prompt,

        task_type=task_type
    )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    print("\n----- FINAL RESULT -----")

    print(
        "Request ID:",
        result["request_id"]
    )

    print(
        "Selected Model:",
        result["model"]
    )

    print(
        "Provider:",
        result["provider"]
    )

    print(
        "Complexity Tier:",
        result["tier"]
    )

    print(
        "Classifier Confidence:",
        f"{result['confidence'] * 100:.2f}%"
    )

    print(
        "Quality Score:",
        result["quality_score"]
    )

    print(
        "Escalated:",
        result["escalated"]
    )

    print(
        "Escalation Count:",
        result["escalation_count"]
    )

    print(
        "Total Cost: $",
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

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    print("\n----- RESPONSE -----")

    print(
        result["output"]
    )

    # --------------------------------------------------------
    # Attempts
    # --------------------------------------------------------

    print("\n----- ATTEMPTS -----")

    for attempt in result["attempts"]:

        print(
            f"{attempt['model']} | "
            f"Cost: ${attempt['cost']:.8f} | "
            f"Latency: "
            f"{attempt['latency_ms']:.2f} ms"
        )

        # Quality score is only available
        # after verification.
        if "quality_score" in attempt:

            print(
                f"Quality: "
                f"{attempt['quality_score']}"
            )

        else:

            print(
                "Quality: Not verified"
            )


print("\n========================================")
print("             TEST COMPLETED")
print("========================================")