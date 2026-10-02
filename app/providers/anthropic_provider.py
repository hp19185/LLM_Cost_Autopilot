import os
import time

import anthropic
from dotenv import load_dotenv

from app.models import ModelConfig
from app.llm_interface import LLMResponse


load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


def send_anthropic_request(
    prompt: str,
    model_config: ModelConfig
) -> LLMResponse:

    start_time = time.perf_counter()

    response = client.messages.create(
        model=model_config.model_id,
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    end_time = time.perf_counter()

    latency_ms = (end_time - start_time) * 1000

    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens

    cost = (
        (input_tokens / 1_000_000)
        * model_config.input_cost_per_million
        +
        (output_tokens / 1_000_000)
        * model_config.output_cost_per_million
    )

    return LLMResponse(
        output=response.content[0].text,
        model_id=model_config.model_id,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        cost=cost
    )