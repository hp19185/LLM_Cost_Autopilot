# ============================================================
# Task Type Detector
# ============================================================

TASK_TYPE_KEYWORDS = {

    "extraction": {
        "extract",
        "find",
        "identify",
        "retrieve",
        "list",
        "emails",
        "email addresses",
        "phone numbers",
        "names",
        "dates"
    },

    "json": {
        "json",
        "json format",
        "json object",
        "json output"
    },

    "summarization": {
        "summarize",
        "summary",
        "summarise",
        "summarization",
        "brief summary",
        "key points"
    },

    "classification": {
        "classify",
        "classification",
        "categorize",
        "category",
        "label",
        "labels"
    },

    "structured_analysis": {
        "analyze",
        "analysis",
        "analyse",
        "evaluate",
        "compare",
        "comparison",
        "pros and cons",
        "advantages and disadvantages"
    },

    "reasoning": {
        "why",
        "explain why",
        "reason",
        "reasoning",
        "derive",
        "prove",
        "justify",
        "solve"
    },

    "architecture": {
        "architecture",
        "architect",
        "design a system",
        "design an application",
        "design a solution",
        "design a platform",
        "build a system",
        "build a platform",
        "build an application",
        "how would you build",
        "how can we build",
        "serve one million users",
        "serve millions of users",
        "millions of users",
        "scalable",
        "scalability",
        "distributed",
        "fault-tolerant",
        "fault tolerant",
        "microservices",
        "end-to-end system",
        "end-to-end architecture"
    },

    "creative_generation": {
        "write a story",
        "creative",
        "poem",
        "poetry",
        "fiction",
        "story",
        "dialogue",
        "script"
    }
}


# ============================================================
# Task Type Detection
# ============================================================

def detect_task_type(prompt: str):

    text = prompt.lower()

    scores = {
        task_type: 0
        for task_type in TASK_TYPE_KEYWORDS
    }

    # --------------------------------------------------------
    # Keyword matching
    # --------------------------------------------------------

    for task_type, keywords in TASK_TYPE_KEYWORDS.items():

        for keyword in keywords:

            if keyword in text:

                scores[task_type] += 1

    # --------------------------------------------------------
    # Find highest-scoring task type
    # --------------------------------------------------------

    best_task_type = max(
        scores,
        key=scores.get
    )

    best_score = scores[best_task_type]

    # --------------------------------------------------------
    # No strong signal
    # --------------------------------------------------------

    if best_score == 0:

        return {
            "task_type": "basic_qa",
            "confidence": 0.50,
            "method": "default"
        }

    # --------------------------------------------------------
    # Calculate simple confidence
    # --------------------------------------------------------

    total_score = sum(
        scores.values()
    )

    confidence = (
        best_score / total_score
        if total_score > 0
        else 0.50
    )

    return {
        "task_type": best_task_type,
        "confidence": confidence,
        "method": "keyword"
    }