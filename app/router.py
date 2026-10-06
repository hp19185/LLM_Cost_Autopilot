from pathlib import Path
import os
import joblib
import pandas as pd

from app.feature_extractor import extract_features
from app.model_registry import ModelRegistry


class ModelRouter:

    def __init__(self):

        # --------------------------------------------------
        # Load model registry
        # --------------------------------------------------

        self.registry = ModelRegistry()

        # --------------------------------------------------
        # Load trained complexity classifier
        # --------------------------------------------------

        base_dir = Path(__file__).resolve().parent.parent

        model_path = (
            base_dir
            / "models"
            / "complexity_classifier.pkl"
        )

        self.classifier = joblib.load(model_path)

        # --------------------------------------------------
        # Tier → Model mapping
        #
        # This is our V1 routing policy.
        # --------------------------------------------------

        deployment_env = os.getenv("DEPLOYMENT_ENV")

        print("DEBUG DEPLOYMENT_ENV from environment:", deployment_env)

        if not deployment_env:
            try:
                import streamlit as st
                deployment_env = st.secrets["DEPLOYMENT_ENV"]
                print("DEBUG DEPLOYMENT_ENV from Streamlit secrets:", deployment_env)
            except Exception as e:
                print("DEBUG Streamlit secrets error:", e)
                deployment_env = "local"

        if deployment_env == "cloud":
            self.routing_map = {
                1: "claude_haiku",
                2: "claude_haiku",
                3: "claude_sonnet",
            }
        else:
            self.routing_map = {
                1: "llama_local",
                2: "claude_haiku",
                3: "claude_sonnet",
            }

    # ======================================================
    # Predict complexity tier
    # ======================================================

    def predict_tier(self, prompt: str):

        features = extract_features(prompt)

        feature_df = pd.DataFrame([features])

        prediction = self.classifier.predict(
            feature_df
        )[0]

        probabilities = self.classifier.predict_proba(
            feature_df
        )[0]

        confidence = float(max(probabilities))

        return int(prediction), confidence

    # ======================================================
    # Select model dynamically
    # ======================================================

    def select_model(self, prompt: str):

        tier, confidence = self.predict_tier(prompt)

        model_name = self.routing_map[tier]

        model_config = self.registry.get_model(
            model_name
        )

        return {
            "tier": tier,
            "confidence": confidence,
            "model_name": model_name,
            "model_config": model_config,
        }