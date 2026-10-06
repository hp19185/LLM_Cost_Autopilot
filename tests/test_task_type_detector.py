import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.task_type_detector import detect_task_type


test_prompts = [
    # Basic QA
    "What is Python?",
    "What is the difference between RAM and ROM?",
    "How does a CPU execute instructions?",

    # Extraction
    "Extract all email addresses from this document.",
    "Find all phone numbers in the following text.",
    "Identify the names of all employees mentioned below.",

    # JSON
    "Convert this information into JSON format.",
    "Return the following student information as a JSON object.",

    # Summarization
    "Summarize this research paper in five bullet points.",
    "Give me a brief summary of this article.",
    "Provide the key points from this report.",

    # Classification
    "Classify these applications as AI or non-AI.",
    "Categorize these customer complaints into appropriate groups.",

    # Structured analysis
    "Analyze the advantages and disadvantages of cloud computing.",
    "What are the pros and cons of using SQL databases?",
    "Compare SQL and NoSQL databases.",

    # Reasoning
    "Why does a neural network need an activation function?",
    "Explain why this algorithm fails on large datasets.",
    "How can we prove that this algorithm is correct?",

    # Architecture
    "Design a scalable architecture for an application serving millions of users.",
    "How would you build a system that serves one million users?",
    "Create an end-to-end architecture for a distributed application.",

    # Creative generation
    "Write a short creative story about artificial intelligence.",
    "Write a poem about robots.",
    "Create a fictional dialogue between two AI systems."
]


for prompt in test_prompts:

    result = detect_task_type(prompt)

    print()
    print("Prompt:", prompt)
    print("Task Type:", result["task_type"])
    print(
        "Confidence:",
        f"{result['confidence'] * 100:.2f}%"
    )
    print("Method:", result["method"])