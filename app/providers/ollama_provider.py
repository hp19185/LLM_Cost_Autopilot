import time

import ollama

from app.models import ModelConfig
from app.llm_interface import LLMResponse


def send_ollama_request(
    prompt: str,
    model_config: ModelConfig
) -> LLMResponse:

    start_time = time.perf_counter()

    response = ollama.chat(
        model=model_config.model_id,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    end_time = time.perf_counter()

    latency_ms = (end_time - start_time) * 1000

    input_tokens = response["prompt_eval_count"]
    output_tokens = response["eval_count"]

    cost = (
        (input_tokens / 1_000_000)
        * model_config.input_cost_per_million
        +
        (output_tokens / 1_000_000)
        * model_config.output_cost_per_million
    )

    return LLMResponse(
        output=response["message"]["content"],
        model_id=model_config.model_id,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        cost=cost
    )