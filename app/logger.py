import hashlib

from app.database import (
    initialize_database,
    log_request
)


# ============================================================
# Initialize database
# ============================================================

initialize_database()


# ============================================================
# Create prompt hash
# ============================================================

def create_prompt_hash(prompt: str) -> str:

    return hashlib.sha256(
        prompt.encode("utf-8")
    ).hexdigest()


# ============================================================
# Log LLM request
# ============================================================

def log_llm_request(

    prompt,

    routing_result,

    response

):

    prompt_hash = create_prompt_hash(
        prompt
    )

    model_config = routing_result[
        "model_config"
    ]

    request_id = log_request(

        prompt_hash=prompt_hash,

        complexity_tier=routing_result[
            "tier"
        ],

        classifier_confidence=routing_result[
            "confidence"
        ],

        model_name=routing_result[
            "model_name"
        ],

        provider=model_config.provider,

        model_id=model_config.model_id,

        input_tokens=response.input_tokens,

        output_tokens=response.output_tokens,

        latency_ms=response.latency_ms,

        cost=response.cost

    )

    return request_id