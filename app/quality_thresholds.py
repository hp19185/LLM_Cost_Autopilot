from dataclasses import dataclass


# ============================================================
# Quality Threshold Configuration
# ============================================================

@dataclass
class QualityThreshold:

    # Minimum acceptable score when an LLM judge is required
    minimum_score: float

    # Whether this task should use an LLM judge
    use_llm_judge: bool

    # Whether deterministic validation can be performed
    deterministic_check: bool


# ============================================================
# Quality Threshold Registry
# ============================================================

QUALITY_THRESHOLDS = {

    # --------------------------------------------------------
    # Tier 1 / Simple tasks
    # --------------------------------------------------------

    "extraction": QualityThreshold(
        minimum_score=1.0,
        use_llm_judge=False,
        deterministic_check=True
    ),

    "json": QualityThreshold(
        minimum_score=1.0,
        use_llm_judge=False,
        deterministic_check=True
    ),

    "basic_qa": QualityThreshold(
        minimum_score=4.0,
        use_llm_judge=True,
        deterministic_check=False
    ),

    # --------------------------------------------------------
    # Tier 2 / Moderate tasks
    # --------------------------------------------------------

    "summarization": QualityThreshold(
        minimum_score=4.0,
        use_llm_judge=True,
        deterministic_check=False
    ),

    "classification": QualityThreshold(
        minimum_score=1.0,
        use_llm_judge=False,
        deterministic_check=True
    ),

    "structured_analysis": QualityThreshold(
        minimum_score=4.0,
        use_llm_judge=True,
        deterministic_check=False
    ),

    # --------------------------------------------------------
    # Tier 3 / Complex tasks
    # --------------------------------------------------------

    "reasoning": QualityThreshold(
        minimum_score=4.0,
        use_llm_judge=True,
        deterministic_check=False
    ),

    "architecture": QualityThreshold(
        minimum_score=4.0,
        use_llm_judge=True,
        deterministic_check=False
    ),

    "creative_generation": QualityThreshold(
        minimum_score=4.0,
        use_llm_judge=True,
        deterministic_check=False
    )
}


# ============================================================
# Get threshold for a task type
# ============================================================

def get_quality_threshold(task_type: str) -> QualityThreshold:

    if task_type not in QUALITY_THRESHOLDS:

        raise ValueError(
            f"Unknown task type: {task_type}"
        )

    return QUALITY_THRESHOLDS[task_type]