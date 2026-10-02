from app.router import ModelRouter
from app.llm_interface import send_request
from app.logger import log_llm_request


# ============================================================
# Create router
# ============================================================

router = ModelRouter()


# ============================================================
# Test prompts
# ============================================================

test_prompts = [

    # ========================================================
    # TIER 1 — SIMPLE
    # ========================================================

    "What is Python?",

    "What is a variable in Python?",

    "What is CPU?",

    "Convert 10 kilometers to meters.",

    "List three Python data types.",


    # ========================================================
    # TIER 2 — MODERATE
    # ========================================================

    "Explain the main advantages of cloud computing.",

    "Summarize the role of machine learning in healthcare.",

    "Compare SQL and NoSQL databases.",

    "Explain how a neural network learns from data.",

    "Classify these applications as AI or non-AI and explain your reasoning.",


    # ========================================================
    # TIER 3 — COMPLEX
    # ========================================================

    "Design a scalable architecture for an application serving millions of users.",

    "Design an end-to-end machine learning system for predicting customer churn.",

    "Develop a fault-tolerant architecture for a distributed application.",

    "Optimize a large-scale data processing system for low latency and high throughput.",

    "Design a multi-agent AI system for automated customer support."
]


# ============================================================
# Run dynamic requests
# ============================================================

print("\n========================================")
print("       DYNAMIC LLM REQUEST TEST")
print("========================================")


for index, prompt in enumerate(
    test_prompts,
    start=1
):

    print("\n----------------------------------------")
    print(f"REQUEST #{index}")

    print("\nPrompt:")
    print(prompt)


    # --------------------------------------------------------
    # Select model dynamically
    # --------------------------------------------------------

    routing_result = router.select_model(prompt)

    selected_model = routing_result["model_config"]


    print("\n----- ROUTING -----")

    print(
        "Complexity Tier:",
        routing_result["tier"]
    )

    print(
        "Classifier Confidence:",
        f"{routing_result['confidence'] * 100:.2f}%"
    )

    print(
        "Selected Model:",
        routing_result["model_name"]
    )

    print(
        "Provider:",
        selected_model.provider
    )

    print(
        "Model ID:",
        selected_model.model_id
    )


    # --------------------------------------------------------
    # Send request using selected model
    # --------------------------------------------------------

    response = send_request(
        prompt=prompt,
        model_config=selected_model
    )

    # --------------------------------------------------------
    # Log request
    # --------------------------------------------------------

    request_id = log_llm_request(
        prompt=prompt,
        routing_result=routing_result,
        response=response
    )

    print(
        "\nRequest ID:",
        request_id
    )
    # --------------------------------------------------------
    # Display response
    # --------------------------------------------------------

    print("\n----- LLM RESPONSE -----")

    print(response.output)


    # --------------------------------------------------------
    # Display metadata
    # --------------------------------------------------------

    print("\n----- METADATA -----")

    print(
        "Model:",
        response.model_id
    )

    print(
        "Input tokens:",
        response.input_tokens
    )

    print(
        "Output tokens:",
        response.output_tokens
    )

    print(
        "Latency:",
        round(response.latency_ms, 2),
        "ms"
    )

    print(
        "Cost: $",
        round(response.cost, 8)
    )