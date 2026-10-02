from app.feature_extractor import extract_features


prompts = [
    "Extract the email addresses from this text.",
    "Summarize this article in five bullet points.",
    "Design a scalable distributed architecture for a banking system.",
]


print("\n----- FEATURE EXTRACTION TEST -----")


for prompt in prompts:

    print("\nPrompt:")
    print(prompt)

    features = extract_features(prompt)

    print("\nFeatures:")

    for name, value in features.items():
        print(f"{name}: {value}")