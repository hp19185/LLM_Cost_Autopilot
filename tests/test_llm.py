from app.model_registry import ModelRegistry
from app.llm_interface import send_request


# --------------------------------------------------
# 1. Test prompt
# --------------------------------------------------

prompt = "Explain what an LLM is in three simple sentences."


# --------------------------------------------------
# 2. Load model registry
# --------------------------------------------------

registry = ModelRegistry()


# --------------------------------------------------
# 3. Display all available models
# --------------------------------------------------

print("\n----- AVAILABLE MODELS -----")

for name, model in registry.list_models().items():

    print(f"\nName: {name}")
    print(f"Provider: {model.provider}")
    print(f"Model ID: {model.model_id}")
    print(
        f"Input cost: "
        f"${model.input_cost_per_million}/1M tokens"
    )
    print(
        f"Output cost: "
        f"${model.output_cost_per_million}/1M tokens"
    )
    print(f"Average latency: {model.average_latency_ms} ms")
    print(f"Quality tier: {model.quality_tier}")


# --------------------------------------------------
# 4. Select a model from the registry
# --------------------------------------------------

selected_model = registry.get_model("llama_local")


print("\n----- SELECTED MODEL -----")
print("Model:", selected_model.model_id)
print("Provider:", selected_model.provider)
print("Quality tier:", selected_model.quality_tier)


# --------------------------------------------------
# 5. Send request through unified interface
# --------------------------------------------------

response = send_request(
    prompt=prompt,
    model_config=selected_model
)


# --------------------------------------------------
# 6. Display LLM response
# --------------------------------------------------

print("\n----- LLM RESPONSE -----")
print(response.output)


# --------------------------------------------------
# 7. Display response metadata
# --------------------------------------------------

print("\n----- METADATA -----")
print("Model:", response.model_id)
print("Input tokens:", response.input_tokens)
print("Output tokens:", response.output_tokens)
print(
    "Latency:",
    round(response.latency_ms, 2),
    "ms"
)
print(
    "Cost: $",
    round(response.cost, 8)
)