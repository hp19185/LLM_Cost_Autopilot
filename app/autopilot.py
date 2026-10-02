import hashlib

from app.router import ModelRouter
from app.llm_interface import send_request
from app.quality_verifier import QualityVerifier
from app.escalation import EscalationManager
from app.feedback import FeedbackManager


from app.database import (
    initialize_database,
    log_request,
    record_feedback,
    update_quality_result,
    update_escalation_result
)

class LLMCostAutopilot:

    def __init__(self):

        self.router = ModelRouter()

        # Quality verifier is kept,
        # but it is NOT used for every response.
        self.verifier = QualityVerifier()

        self.escalation_manager = EscalationManager()
        self.feedback_manager = FeedbackManager()

        # Initialize database
        initialize_database()

        # Keep active requests in memory
        self.active_requests = {}

    # ======================================================
    # Process one request
    # ======================================================

    def process_request(self, prompt, task_type=None):

        # --------------------------------------------------
        # 1. Dynamic routing
        # --------------------------------------------------

        routing_result = self.router.select_model(prompt)

        current_model_name = routing_result["model_name"]

        current_model = routing_result["model_config"]

        tier = routing_result["tier"]

        confidence = routing_result["confidence"]

        # --------------------------------------------------
        # 2. Send request to selected model
        # --------------------------------------------------

        response = send_request(prompt=prompt, model_config=current_model)

        # --------------------------------------------------
        # 3. Generate prompt hash
        # --------------------------------------------------

        prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()

        # --------------------------------------------------
        # 4. Save request in database
        # --------------------------------------------------

        request_id = log_request(
            prompt_hash=prompt_hash,
            complexity_tier=tier,
            classifier_confidence=confidence,
            model_name=current_model_name,
            provider=current_model.provider,
            model_id=current_model.model_id,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            latency_ms=response.latency_ms,
            cost=response.cost,
            quality_score=None,
            escalated=False,
            escalated_model=None
        )

        # --------------------------------------------------
        # 5. Keep request information for feedback
        # --------------------------------------------------

        self.active_requests[request_id] = {
            "prompt": prompt,
            "task_type": task_type,
            "model_name": current_model_name,
            "model_config": current_model,
            "tier": tier,
            "confidence": confidence,
            "response": response,
            "total_cost": response.cost,
            "attempts": [
                {
                    "model": current_model_name,
                    "model_id": current_model.model_id,
                    "cost": response.cost,
                    "latency_ms": response.latency_ms
                }
            ]
        }

        # --------------------------------------------------
        # 6. Return response immediately
        # --------------------------------------------------
        return {
            "request_id": request_id,
            "output": response.output,
            "model": current_model_name,
            "model_id": current_model.model_id,
            "provider": current_model.provider,
            "tier": tier,
            "confidence": confidence,
            "cost": response.cost,
            "latency_ms": response.latency_ms,
            "quality_score": None,
            "escalated": False,
            "escalation_count": 0,
            "attempts":
                self.active_requests[request_id]["attempts"]
        }

    # ======================================================
    # Process user feedback
    # ======================================================

    def submit_feedback(self, request_id, feedback):
        feedback = feedback.lower().strip()

        if feedback not in ["positive","negative"]:
            raise ValueError("Feedback must be 'positive' or 'negative'")

        # --------------------------------------------------
        # Save feedback
        # --------------------------------------------------

        record_feedback(request_id=request_id, feedback=feedback)

        # --------------------------------------------------
        # Positive feedback
        # --------------------------------------------------

        if feedback == "positive":
            update_escalation_result(
                request_id=request_id,
                user_consent=False,
                escalated=False
            )
            return {
                "request_id": request_id,
                "feedback": "positive",
                "verification_required": False,
                "escalated": False,
                "message":
                    "Response accepted. "
                    "No quality verification required."
            }

        # --------------------------------------------------
        # Negative feedback
        # --------------------------------------------------

        request = self.active_requests.get(request_id)

        if request is None:
            return {
                "request_id": request_id,
                "feedback": "negative",
                "verification_required": True,
                "escalated": False,
                "message":
                    "Negative feedback recorded, "
                    "but request details are no longer "
                    "available in the current session."
            }

        # --------------------------------------------------
        # Verify only after negative feedback
        # --------------------------------------------------

        verification = self.verifier.verify(
            task_type=request["task_type"],
            original_prompt=request["prompt"],
            response=request["response"].output
        )
        update_quality_result(
            request_id=request_id,
            quality_score=verification["score"],
            quality_passed=verification["passed"],
            verification_method=verification["method"]
        )
        # --------------------------------------------------
        # Quality passed
        # --------------------------------------------------

        if verification["passed"]:
            return {
                "request_id": request_id,
                "feedback": "negative",
                "verification_required": True,
                "quality_verified": True,
                "quality_score": verification["score"],
                "quality_passed": True,
                "verification_method": verification["method"],
                "escalation_available": False,
                "current_model": request["model_name"],
                "next_model": None,
                "escalated": False,
                "message":
                    "User reported a problem, "
                    "but the quality verifier "
                    "did not identify a quality failure."
            }

        # --------------------------------------------------
        # Quality failed → escalation is available
        # --------------------------------------------------

        current_model_name = request["model_name"]

        next_model = (
            self.escalation_manager.get_next_model(current_model_name)
        )

        # --------------------------------------------------
        # No higher model available
        # --------------------------------------------------

        if next_model is None:
            return {
                "request_id": request_id,
                "feedback": "negative",
                "quality_verified": True,
                "quality_score": verification["score"],
                "quality_passed": False,
                "escalation_available": False,
                "current_model": current_model_name,
                "next_model": None,
                "message":
                    "Quality verification failed, "
                    "but no higher-tier model is available."
            }

        # --------------------------------------------------
        # Higher model is available
        #
        # IMPORTANT:
        # Do NOT escalate automatically.
        # The user must give consent.
        # --------------------------------------------------

        next_model_name = (self._get_model_name(next_model))

        return {
            "request_id": request_id,
            "feedback": "negative",
            "quality_verified": True,
            "quality_score": verification["score"],
            "quality_passed": False,
            "escalation_available": True,
            "current_model": current_model_name,
            "next_model": next_model_name,
            "next_model_id": next_model.model_id,
            "next_provider": next_model.provider,
            "message":
                "Quality verification failed. "
                "A higher-tier model is available. "
                "User consent is required before escalation."
        }

    # ======================================================
    # Approve escalation after user consent
    # ======================================================

    def approve_escalation(self, request_id):

        # --------------------------------------------------
        # Get original request
        # --------------------------------------------------

        request = self.active_requests.get(request_id)

        if request is None:
            raise ValueError(f"Request {request_id} not found.")

        # --------------------------------------------------
        # Get current model
        # --------------------------------------------------

        current_model_name = request["model_name"]

        current_model = (self.router.registry.get_model(current_model_name))

        # --------------------------------------------------
        # Find next higher-tier model
        # --------------------------------------------------

        next_model = (
            self.escalation_manager
            .get_next_model(
                current_model_name
            )
        )

        if next_model is None:

            return {
                "request_id": request_id,
                "escalated": False,
                "message":
                    "No higher-tier model is available."
            }

        # --------------------------------------------------
        # Send request to higher-tier model
        # --------------------------------------------------

        response = send_request(
            prompt=request["prompt"],
            model_config=next_model
        )

        # --------------------------------------------------
        # Return escalated response
        # --------------------------------------------------

        update_escalation_result(
            request_id=request_id,
            user_consent=True,
            escalated=True,
            escalated_model=self._get_model_name(next_model),
            original_cost=request["response"].cost,
            escalated_cost=response.cost,
            additional_cost=response.cost,
            total_cost=request["response"].cost + response.cost
        )

        return {
            "request_id": request_id,
            "escalated": True,
            "original_model": current_model_name,
            "escalated_model": self._get_model_name(next_model),
            "model_id": next_model.model_id,
            "provider": next_model.provider,
            "output": response.output,
            "original_cost": request["response"].cost,
            "escalated_cost": response.cost,
            "additional_cost": response.cost - request["response"].cost,
            "total_cost": request["response"].cost + response.cost,
            "cost": response.cost,
            "latency_ms": response.latency_ms
        }

    # ======================================================
    # Find registry name from model configuration
    # ======================================================

    def _get_model_name(
        self,
        model_config
    ):

        for name, model in (
            self.router.registry
            .list_models()
            .items()
        ):

            if model.model_id == model_config.model_id:
                return name

        raise ValueError(
            f"Model {model_config.model_id} "
            f"not found in registry."
        )