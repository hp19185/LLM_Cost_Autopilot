from pathlib import Path

import yaml

from app.models import ModelConfig


class ModelRegistry:

    def __init__(self, config_path: str = "config/models.yaml"):
        self.config_path = Path(config_path)
        self.models = {}

        self._load_models()

    def _load_models(self):

        with open(self.config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)

        for name, model_data in config["models"].items():

            self.models[name] = ModelConfig(
                provider=model_data["provider"],
                model_id=model_data["model_id"],
                input_cost_per_million=model_data[
                    "input_cost_per_million"
                ],
                output_cost_per_million=model_data[
                    "output_cost_per_million"
                ],
                average_latency_ms=model_data[
                    "average_latency_ms"
                ],
                quality_tier=model_data["quality_tier"]
            )

    def get_model(self, name: str) -> ModelConfig:

        if name not in self.models:
            raise ValueError(
                f"Model '{name}' not found in registry."
            )

        return self.models[name]

    def list_models(self):

        return self.models