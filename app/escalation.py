from app.model_registry import ModelRegistry


class EscalationManager:

    def __init__(self):

        self.registry = ModelRegistry()

        # --------------------------------------------------
        # Escalation hierarchy
        # --------------------------------------------------
        #
        # Each model points to the next more capable model.
        #
        # llama_local → claude_haiku → claude_sonnet
        #
        # claude_sonnet → None
        #
        # --------------------------------------------------

        self.escalation_map = {

            "llama_local": "claude_haiku",

            "claude_haiku": "claude_sonnet",

            "claude_sonnet": None
        }

    # ======================================================
    # Get next model
    # ======================================================

    def get_next_model(self, current_model_name):

        next_model_name = self.escalation_map.get(
            current_model_name
        )

        if next_model_name is None:

            return None

        return self.registry.get_model(
            next_model_name
        )

    # ======================================================
    # Check whether escalation is possible
    # ======================================================

    def can_escalate(self, current_model_name):

        return (
            self.escalation_map.get(
                current_model_name
            ) is not None
        )

    # ======================================================
    # Calculate escalation cost
    # ======================================================

    def calculate_cost_delta(
        self,
        original_cost,
        escalated_cost
    ):

        return escalated_cost - original_cost