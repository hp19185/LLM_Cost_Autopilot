from app.autopilot import LLMCostAutopilot


def run_dashboard_test():
    autopilot = LLMCostAutopilot()

    test_prompts = [
        # Tier 1
        "What is Python?",
        "What is a variable in Python?",

        # Tier 2
        "Summarize the following idea in five bullet points: machine learning helps computers learn patterns from data.",
        "Explain the main advantages of cloud computing in five bullet points.",

        # Tier 3
        "Design a scalable architecture for a web application serving millions of users.",
        "Compare SQL and NoSQL databases for a large-scale distributed application and explain when each should be used."
    ]

    print("\n" + "=" * 70)
    print("        DASHBOARD TEST DATA GENERATION")
    print("=" * 70)

    for index, prompt in enumerate(test_prompts, start=1):

        print(f"\n{'-' * 70}")
        print(f"REQUEST {index}")
        print(f"Prompt: {prompt}")

        result = autopilot.process_request(prompt)

        print(f"Model      : {result['model']}")
        print(f"Provider   : {result['provider']}")
        print(f"Cost       : $ {result['cost']:.6f}")
        print(f"Latency    : {result['latency_ms']:.2f} ms")

    print("\n" + "=" * 70)
    print("Dashboard test data generation completed.")
    print("=" * 70)


if __name__ == "__main__":
    run_dashboard_test()