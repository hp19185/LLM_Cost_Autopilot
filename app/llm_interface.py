from dataclasses import dataclass

from app.models import ModelConfig


@dataclass
class LLMResponse:
    output: str
    model_id: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    cost: float


def send_request(
    prompt: str,
    model_config: ModelConfig
) -> LLMResponse:

    if model_config.provider == "openai":

        from app.providers.openai_provider import send_openai_request

        return send_openai_request(
            prompt,
            model_config
        )
    elif model_config.provider == "anthropic":

        from app.providers.anthropic_provider import send_anthropic_request

        return send_anthropic_request(
            prompt,
            model_config
        )
    elif model_config.provider == "ollama":

        from app.providers.ollama_provider import send_ollama_request

        return send_ollama_request(
            prompt,
            model_config
        )
    else:
        raise ValueError(
            f"Unsupported provider: {model_config.provider}"
        )