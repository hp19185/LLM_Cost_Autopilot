import json
import re

from app.model_registry import ModelRegistry
from app.llm_interface import send_request
from app.quality_thresholds import get_quality_threshold


class QualityVerifier:

    def __init__(self):

        # --------------------------------------------------
        # Load model registry
        # --------------------------------------------------

        self.registry = ModelRegistry()

        # --------------------------------------------------
        # Highest quality model used only when an
        # LLM-as-judge evaluation is actually required
        # --------------------------------------------------

        self.judge_model = self.registry.get_model(
            "claude_sonnet"
        )

    # ======================================================
    # Main verification function
    # ======================================================

    def verify(
        self,
        task_type,
        original_prompt,
        response,
        expected_output=None
    ):

        # --------------------------------------------------
        # Get quality rules
        # --------------------------------------------------

        threshold = get_quality_threshold(
            task_type
        )

        # --------------------------------------------------
        # Deterministic verification
        # --------------------------------------------------

        if threshold.deterministic_check:

            result = self._deterministic_check(
                task_type=task_type,
                response=response,
                expected_output=expected_output
            )

            return result

        # --------------------------------------------------
        # LLM-as-judge verification
        # --------------------------------------------------

        if threshold.use_llm_judge:

            return self._llm_judge_check(
                task_type=task_type,
                original_prompt=original_prompt,
                response=response,
                minimum_score=threshold.minimum_score
            )

        # --------------------------------------------------
        # Fallback
        # --------------------------------------------------

        return {
            "passed": True,
            "score": None,
            "method": "none",
            "reason": "No verification method configured.",
            "judge_model": None,
            "judge_latency_ms": 0,
            "judge_cost": 0.0
        }

    # ======================================================
    # Deterministic checks
    # ======================================================

    def _deterministic_check(
        self,
        task_type,
        response,
        expected_output=None
    ):

        # --------------------------------------------------
        # JSON validation
        # --------------------------------------------------

        if task_type == "json":

            try:

                cleaned_response = response.strip()

                # Remove Markdown code fences
                if cleaned_response.startswith("```"):

                    lines = cleaned_response.splitlines()

                    # Remove first line: ```json or ```
                    if lines:
                        lines = lines[1:]

                    # Remove last line: ```
                    if lines and lines[-1].strip() == "```":
                        lines = lines[:-1]

                    cleaned_response = "\n".join(lines).strip()

                # Validate JSON
                json.loads(cleaned_response)

                return {
                    "passed": True,
                    "score": 5.0,
                    "method": "deterministic",
                    "reason": "Response contains valid JSON.",
                    "judge_model": None,
                    "judge_latency_ms": 0,
                    "judge_cost": 0.0
                }

            except json.JSONDecodeError:

                return {
                    "passed": False,
                    "score": 1.0,
                    "method": "deterministic",
                    "reason": "Response is not valid JSON.",
                    "judge_model": None,
                    "judge_latency_ms": 0,
                    "judge_cost": 0.0
                }

        # --------------------------------------------------
        # Classification validation
        # --------------------------------------------------

        if task_type == "classification":

            if expected_output is None:

                return {
                    "passed": False,
                    "score": None,
                    "method": "deterministic",
                    "reason": (
                        "Expected output is required "
                        "for classification validation."
                    ),
                    "judge_model": None,
                    "judge_latency_ms": 0,
                    "judge_cost": 0.0
                }

            actual = response.strip().lower()
            expected = str(
                expected_output
            ).strip().lower()

            passed = actual == expected

            return {
                "passed": passed,
                "score": 5.0 if passed else 1.0,
                "method": "deterministic",
                "reason": (
                    "Classification matches expected output."
                    if passed
                    else
                    "Classification does not match expected output."
                ),
                "judge_model": None,
                "judge_latency_ms": 0,
                "judge_cost": 0.0
            }

        # --------------------------------------------------
        # Extraction validation
        # --------------------------------------------------

        if task_type == "extraction":

            if expected_output is None:

                return {
                    "passed": False,
                    "score": None,
                    "method": "deterministic",
                    "reason": (
                        "Expected output is required "
                        "for extraction validation."
                    ),
                    "judge_model": None,
                    "judge_latency_ms": 0,
                    "judge_cost": 0.0
                }

            missing_items = []

            for item in expected_output:

                if str(item).lower() not in response.lower():

                    missing_items.append(item)

            passed = len(missing_items) == 0

            return {
                "passed": passed,
                "score": 5.0 if passed else 1.0,
                "method": "deterministic",
                "reason": (
                    "All expected items were found."
                    if passed
                    else
                    f"Missing items: {missing_items}"
                ),
                "judge_model": None,
                "judge_latency_ms": 0,
                "judge_cost": 0.0
            }

        # --------------------------------------------------
        # Fallback deterministic check
        # --------------------------------------------------

        return {
            "passed": bool(response.strip()),
            "score": 5.0 if response.strip() else 1.0,
            "method": "deterministic",
            "reason": (
                "Response is non-empty."
                if response.strip()
                else
                "Response is empty."
            ),
            "judge_model": None,
            "judge_latency_ms": 0,
            "judge_cost": 0.0
        }

    # ======================================================
    # LLM-as-judge verification
    # ======================================================

    def _llm_judge_check(
        self,
        task_type,
        original_prompt,
        response,
        minimum_score
    ):

        evaluation_prompt = f"""
        You are a strict quality evaluator for an LLM routing system.

        Your job is to determine whether the response is good enough
        to be accepted from a lower-cost model.

        TASK TYPE:
        {task_type}

        ORIGINAL USER PROMPT:
        {original_prompt}

        LLM RESPONSE:
        {response}

        Evaluate the response using these four criteria:

        1. RELEVANCE
           Does the response directly answer the user's request?

        2. CORRECTNESS
           Is the information technically and factually correct?

        3. COMPLETENESS
           Does the response fully satisfy the requested task?
           Penalize incomplete, truncated, or missing sections.

        4. INSTRUCTION FOLLOWING
           Did the response follow the requested format,
           number of items, constraints, and other instructions?

        Scoring:

        5 = Excellent
            Fully correct, complete, relevant, and follows instructions.

        4 = Good
            Correct and useful with only minor omissions.

        3 = Acceptable
            Generally useful but has noticeable weaknesses,
            omissions, or minor errors.

        2 = Poor
            Significant problems, missing important information,
            or partially fails the requested task.

        1 = Very poor
            Incorrect, irrelevant, incomplete, or fails the task.

        IMPORTANT:
        A response that is cut off, incomplete, or missing major
        requested components MUST NOT receive a score of 5.

        Return ONLY:

        SCORE: <number>
        REASON: <short explanation>
        """

        # --------------------------------------------------
        # Call judge model
        # --------------------------------------------------

        judge_response = send_request(
            prompt=evaluation_prompt,
            model_config=self.judge_model
        )

        # --------------------------------------------------
        # Extract score
        # --------------------------------------------------

        score = self._extract_score(
            judge_response.output
        )

        # --------------------------------------------------
        # Determine pass/fail
        # --------------------------------------------------

        passed = (
            score is not None
            and score >= minimum_score
        )

        return {
            "passed": passed,
            "score": score,
            "method": "llm_judge",
            "reason": judge_response.output,
            "judge_model": self.judge_model.model_id,
            "judge_latency_ms": judge_response.latency_ms,
            "judge_cost": judge_response.cost
        }

    # ======================================================
    # Extract score from judge response
    # ======================================================

    def _extract_score(
        self,
        evaluation_output
    ):

        for line in evaluation_output.splitlines():

            line = line.strip()

            if line.startswith("SCORE:"):

                score_text = (
                    line
                    .replace("SCORE:", "")
                    .strip()
                )

                # ------------------------------------------
                # Extract numeric value
                # ------------------------------------------

                match = re.search(
                    r"\d+(?:\.\d+)?",
                    score_text
                )

                if match:

                    score = float(
                        match.group()
                    )

                    if 1 <= score <= 5:

                        return score

        return None