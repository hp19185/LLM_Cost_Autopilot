from pathlib import Path

import joblib
import pandas as pd

from app.feature_extractor import extract_features


BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "complexity_classifier.pkl"

classifier = joblib.load(MODEL_PATH)


test_prompts = [
    "Summarize the following research paper in five bullet points.",
    "Summarize the following idea in five bullet points: "
    "machine learning helps computers learn patterns from data.",
    "Explain the main advantages of cloud computing in five bullet points.",
    "Compare these two database systems and explain their main differences.",
    "Design a scalable architecture for an application serving millions of users."
]


print("\n" + "=" * 80)
print("           CLASSIFIER DIAGNOSTIC")
print("=" * 80)


for index, prompt in enumerate(test_prompts, start=1):

    features = extract_features(prompt)

    feature_df = pd.DataFrame([features])

    prediction = classifier.predict(feature_df)[0]

    probabilities = classifier.predict_proba(feature_df)[0]

    confidence = max(probabilities)

    print("\n" + "-" * 80)
    print(f"TEST #{index}")

    print("\nPrompt:")
    print(prompt)

    print("\nPrediction:")
    print("Tier      :", prediction)
    print("Confidence:", f"{confidence * 100:.2f}%")

    print("\nFeatures:")

    for feature_name, feature_value in features.items():
        print(f"{feature_name:30}: {feature_value}")


print("\n" + "=" * 80)
print("       DIAGNOSTIC COMPLETED")
print("=" * 80)