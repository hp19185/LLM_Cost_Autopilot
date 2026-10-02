import time

from app.model_registry import ModelRegistry
from app.llm_interface import send_request


registry = ModelRegistry()

model = registry.get_model("llama_local")

prompt = "What is Python? Answer in exactly two sentences."


print("\n========================================")
print("       OLLAMA LATENCY TEST")
print("========================================")

print("\nModel:", model.model_id)
print("Provider:", model.provider)

start = time.perf_counter()

response = send_request(
    prompt=prompt,
    model_config=model
)

end = time.perf_counter()

python_latency = (end - start) * 1000


print("\n----- RESPONSE -----")
print(response.output)

print("\n----- LATENCY -----")

print(
    "send_request reported:",
    round(response.latency_ms, 2),
    "ms"
)

print(
    "Python measured:",
    round(python_latency, 2),
    "ms"
)

print(
    "\nDifference:",
    round(
        python_latency - response.latency_ms,
        2
    ),
    "ms"
)