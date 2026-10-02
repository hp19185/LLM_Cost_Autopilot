from app.router import ModelRouter


# ============================================================
# Create router
# ============================================================

router = ModelRouter()


# ============================================================
# Test prompts
# ============================================================

test_prompts = [

    "What is Python?",

    "Summarize this research paper in five bullet points.",

    "Design a scalable architecture for an application serving millions of users.",

    "Extract all email addresses from this paragraph.",

    "Analyze this customer feedback and identify the major problems.",

]


# ============================================================
# Test dynamic routing
# ============================================================

print("\n========================================")
print("       DYNAMIC MODEL ROUTING TEST")
print("========================================")


for index, prompt in enumerate(
    test_prompts,
    start=1
):

    result = router.select_model(prompt)

    model = result["model_config"]


    print("\n----------------------------------------")

    print(f"Test #{index}")

    print("\nPrompt:")
    print(prompt)

    print("\nRouting Result:")

    print(
        "Complexity Tier:",
        result["tier"]
    )

    print(
        "Classifier Confidence:",
        f"{result['confidence'] * 100:.2f}%"
    )

    print(
        "Selected Model:",
        result["model_name"]
    )

    print(
        "Provider:",
        model.provider
    )

    print(
        "Model ID:",
        model.model_id
    )

    print(
        "Quality Tier:",
        model.quality_tier
    )

    print(
        "Input Cost:",
        f"${model.input_cost_per_million}/1M tokens"
    )

    print(
        "Output Cost:",
        f"${model.output_cost_per_million}/1M tokens"
    )