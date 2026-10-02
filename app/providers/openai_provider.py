import os
import time

from openai import OpenAI
from dotenv import load_dotenv

from app.models import ModelConfig
from app.llm_interface import LLMResponse


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def send_openai_request(
    prompt: str,
    model_config: ModelConfig
) -> LLMResponse:

    start_time = time.perf_counter()

    response = client.responses.create(
        model=model_config.model_id,
        input=prompt
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
        output=response.output_text,
        model_id=model_config.model_id,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        cost=cost
    )