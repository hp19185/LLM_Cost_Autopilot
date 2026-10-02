import re


# ============================================================
# Keyword groups
# ============================================================

COMPLEXITY_KEYWORDS = {
    "analyze",
    "analysis",
    "compare",
    "evaluate",
    "design",
    "develop",
    "optimize",
    "optimization",
    "strategy",
    "architecture",
    "trade-off",
    "trade-offs",
    "justify",
    "justification",
    "comprehensive",
    "multi-step",
    "solve",
}


# Simple task indicators
SIMPLE_TASK_KEYWORDS = {
    "extract",
    "list",
    "find",
    "identify",
    "count",
    "convert",
    "rewrite",
    "correct",
    "translate",
    "format",
    "sort",
    "remove",
}


# Moderate task indicators
MODERATE_TASK_KEYWORDS = {
    "summarize",
    "summary",
    "classify",
    "categorize",
    "report",
    "evaluate",
    "compare",
    "analyze",
    "explain"
}


# Complex task indicators
COMPLEX_TASK_KEYWORDS = {
    "design",
    "develop",
    "optimize",
    "architecture",
    "strategy",
    "justify",
    "solve",
    "scalable",
    "distributed",
    "production",
    "end-to-end",
    "fault-tolerant",
    "multi-agent",
}


# ============================================================
# Helper function
# ============================================================

def count_keywords(text: str, keywords: set) -> int:

    count = 0

    for keyword in keywords:

        if re.search(
            rf"\b{re.escape(keyword)}\b",
            text
        ):
            count += 1

    return count


# ============================================================
# Main feature extraction function
# ============================================================

def extract_features(prompt: str) -> dict:
    """
    Extract numerical features from a user prompt.

    These features are used by the complexity classifier.
    """

    prompt_lower = prompt.lower()

    # --------------------------------------------------------
    # Basic text features
    # --------------------------------------------------------

    words = prompt.split()

    word_count = len(words)

    character_count = len(prompt)

    token_count = max(
        1,
        int(word_count * 1.3)
    )

    sentence_count = len(
        re.findall(
            r"[.!?]+",
            prompt
        )
    )


    # --------------------------------------------------------
    # Task type features
    # --------------------------------------------------------

    simple_task_count = count_keywords(
        prompt_lower,
        SIMPLE_TASK_KEYWORDS
    )

    moderate_task_count = count_keywords(
        prompt_lower,
        MODERATE_TASK_KEYWORDS
    )

    complex_task_count = count_keywords(
        prompt_lower,
        COMPLEX_TASK_KEYWORDS
    )


    # --------------------------------------------------------
    # General complexity keywords
    # --------------------------------------------------------

    keyword_count = count_keywords(
        prompt_lower,
        COMPLEXITY_KEYWORDS
    )


    # --------------------------------------------------------
    # Instruction count
    # --------------------------------------------------------

    instruction_words = [
        "extract",
        "convert",
        "rewrite",
        "correct",
        "translate",
        "summarize",
        "classify",
        "analyze",
        "compare",
        "design",
        "develop",
        "evaluate",
        "identify",
        "list",
        "create",
        "solve",
        "optimize",
        "format",
        "find",
    ]

    instruction_count = sum(
        1
        for word in instruction_words
        if re.search(
            rf"\b{re.escape(word)}\b",
            prompt_lower
        )
    )


    # --------------------------------------------------------
    # Constraint features
    # --------------------------------------------------------

    constraint_words = [
        "must",
        "should",
        "required",
        "constraint",
        "constraints",
        "under",
        "considering",
        "while",
        "without",
        "minimum",
        "maximum",
        "limited",
    ]

    constraint_count = sum(
        1
        for word in constraint_words
        if re.search(
            rf"\b{re.escape(word)}\b",
            prompt_lower
        )
    )


    # --------------------------------------------------------
    # Requirement indicators
    # --------------------------------------------------------

    requirement_words = [
        "and",
        "also",
        "include",
        "including",
        "consider",
        "provide",
        "explain",
        "justify",
        "compare",
    ]

    requirement_count = sum(
        1
        for word in requirement_words
        if re.search(
            rf"\b{re.escape(word)}\b",
            prompt_lower
        )
    )


    # --------------------------------------------------------
    # Context detection
    # --------------------------------------------------------

    context_indicators = [
        "following",
        "provided",
        "given",
        "below",
        "this text",
        "this article",
        "this dataset",
        "this document",
        "these",
        "the provided",
    ]

    has_context = int(
        any(
            indicator in prompt_lower
            for indicator in context_indicators
        )
    )


    # --------------------------------------------------------
    # Output format complexity
    # --------------------------------------------------------

    output_format_indicators = [
        "json",
        "csv",
        "table",
        "bullet points",
        "report",
        "structured",
        "format",
        "markdown",
    ]

    output_format_complexity = sum(
        1
        for indicator in output_format_indicators
        if indicator in prompt_lower
    )


    # --------------------------------------------------------
    # Reasoning indicators
    # --------------------------------------------------------

    reasoning_indicators = [
        "because",
        "why",
        "reason",
        "explain",
        "justify",
        "trade-off",
        "trade-offs",
        "step-by-step",
        "reasoning",
    ]

    reasoning_indicator = sum(
        1
        for indicator in reasoning_indicators
        if indicator in prompt_lower
    )


    # --------------------------------------------------------
    # Comparison indicator
    # --------------------------------------------------------

    comparison_indicator = int(
        any(
            word in prompt_lower
            for word in [
                "compare",
                "comparison",
                "difference",
                "differences",
                "versus",
                "vs",
            ]
        )
    )


    # --------------------------------------------------------
    # Multi-step indicator
    # --------------------------------------------------------

    multi_step_indicator = int(
        any(
            phrase in prompt_lower
            for phrase in [
                "multi-step",
                "step-by-step",
                "multiple steps",
                "end-to-end",
                "complete solution",
                "comprehensive",
            ]
        )
    )


    # --------------------------------------------------------
    # Question indicator
    # --------------------------------------------------------

    has_question = int(
        "?" in prompt
    )


    # --------------------------------------------------------
    # Return all features
    # --------------------------------------------------------

    return {

        # Task type
        "simple_task_count": simple_task_count,
        "moderate_task_count": moderate_task_count,
        "complex_task_count": complex_task_count,

        # Complexity
        "keyword_count": keyword_count,
        "instruction_count": instruction_count,

        # Requirements
        "constraint_count": constraint_count,
        "requirement_count": requirement_count,

        # Context
        "has_context": has_context,

        # Output
        "output_format_complexity": output_format_complexity,

        # Reasoning
        "reasoning_indicator": reasoning_indicator,

        # Comparison
        "comparison_indicator": comparison_indicator,

        # Multi-step
        "multi_step_indicator": multi_step_indicator,

        # Question
        "has_question": has_question,
    }