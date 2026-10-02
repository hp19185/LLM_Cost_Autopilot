from dataclasses import dataclass


@dataclass
class ModelConfig:
    provider: str
    model_id: str
    input_cost_per_million: float
    output_cost_per_million: float
    average_latency_ms: float
    quality_tier: str