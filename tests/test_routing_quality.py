from app.router import ModelRouter


# ============================================================
# Initialize router
# ============================================================

router = ModelRouter()


print("\n========================================")
print("          ROUTING DIAGNOSTIC")
print("========================================")


# ============================================================
# Test cases
# ============================================================

test_cases = [

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
# Process test cases
# ============================================================

for index, prompt in enumerate(test_cases, start=1):

    print("\n----------------------------------------")
    print(f"REQUEST #{index}")
    print("----------------------------------------")

    print("Prompt:")
    print(prompt)

    # --------------------------------------------------------
    # Dynamic routing
    # --------------------------------------------------------

    routing_result = router.select_model(prompt)

    selected_model = routing_result["model_config"]

    print("\n----- ROUTING RESULT -----")

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


print("\n========================================")
print("       ROUTING DIAGNOSTIC COMPLETED")
print("========================================")