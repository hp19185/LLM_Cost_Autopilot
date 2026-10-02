class FeedbackManager:

    # ============================================================
    # Process user feedback
    # ============================================================

    def process_feedback(self, feedback):

        feedback = feedback.strip().lower()

        if feedback == "y":

            return {
                "valid": True,
                "feedback": "positive",
                "requires_verification": False
            }

        elif feedback == "n":

            return {
                "valid": True,
                "feedback": "negative",
                "requires_verification": True
            }

        else:

            return {
                "valid": False,
                "feedback": None,
                "requires_verification": False
            }