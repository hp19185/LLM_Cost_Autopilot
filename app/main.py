import sys
from pathlib import Path

import streamlit as st


# Add project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.autopilot import LLMCostAutopilot


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="LLM Cost Autopilot",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# Initialize Autopilot
# ============================================================

@st.cache_resource
def get_autopilot():
    return LLMCostAutopilot()

autopilot = get_autopilot()


# ============================================================
# Header
# ============================================================

st.title("🤖 LLM Cost Autopilot")

st.write(
    "Enter a prompt and let the system automatically "
    "select an appropriate LLM based on task complexity."
)


# ============================================================
# Prompt Input
# ============================================================

st.subheader("Prompt")

prompt = st.text_area(
    "Enter your prompt:",
    height=150,
    placeholder="Example: Explain how neural networks learn from data."
)


# ============================================================
# Submit Prompt
# ============================================================

if st.button("Submit Prompt", type="primary"):

    if not prompt.strip():

        st.warning("Please enter a prompt.")

    else:

        with st.spinner(
            "Analyzing prompt and generating response..."
        ):

            result = autopilot.process_request(
                prompt.strip()
            )

        # ----------------------------------------------------
        # Save result in session state
        # ----------------------------------------------------

        st.session_state["last_result"] = result


# ============================================================
# Display Result
# ============================================================

if "last_result" in st.session_state:

    result = st.session_state["last_result"]

    # --------------------------------------------------------
    # Request Information
    # --------------------------------------------------------

    st.subheader("Request Information")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Complexity Tier",
        result["tier"]
    )

    col2.metric(
        "Classifier Confidence",
        f"{result['confidence'] * 100:.2f}%"
    )

    col3.metric(
        "Detected Task Type",
        result["task_type"]
    )

    col4.metric(
        "Task-Type Confidence",
        f"{result['task_type_confidence'] * 100:.2f}%"
    )

    st.caption(
        f"Selected Model: {result['model']}"
    )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    st.subheader("Response")

    st.markdown(
        result["output"]
    )

    # --------------------------------------------------------
    # Request Statistics
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Cost",
        f"${result['cost']:.6f}"
    )

    col2.metric(
        "Latency",
        f"{result['latency_ms']:.0f} ms"
    )

    col3.metric(
        "Request ID",
        result["request_id"]
    )

    # --------------------------------------------------------
    # Feedback
    # --------------------------------------------------------

    st.subheader("Was this response helpful?")

    feedback_col1, feedback_col2 = st.columns(2)

    with feedback_col1:

        if st.button(
            "👍 Helpful",
            key="positive_feedback"
        ):

            feedback_result = autopilot.submit_feedback(
                result["request_id"],
                "positive"
            )

            st.success(
                feedback_result["message"]
            )

    with feedback_col2:

        if st.button(
            "👎 Not Helpful",
            key="negative_feedback"
        ):

            feedback_result = autopilot.submit_feedback(
                result["request_id"],
                "negative"
            )

            if feedback_result.get("quality_passed"):

                st.info(
                    "The response passed quality verification. "
                    "No escalation is required."
                )

            elif feedback_result.get(
                "escalation_available"
            ):

                st.warning(
                    "The response did not pass quality verification."
                )

                st.session_state[
                    "escalation_request_id"
                ] = result["request_id"]

                st.session_state[
                    "escalation_message"
                ] = feedback_result["message"]

            else:

                st.info(
                    feedback_result["message"]
                )


# ============================================================
# Escalation Consent
# ============================================================

if "escalation_request_id" in st.session_state:

    st.subheader("Escalation")

    st.warning(
        st.session_state.get(
            "escalation_message",
            "A higher-capability model is available."
        )
    )

    if st.button(
        "Use Higher Model",
        type="primary",
        key="approve_escalation"
    ):

        request_id = st.session_state[
            "escalation_request_id"
        ]

        with st.spinner(
            "Generating improved response..."
        ):

            escalation_result = (
                autopilot.approve_escalation(
                    request_id
                )
            )

        if escalation_result.get("escalated"):

            st.success(
                "Response successfully escalated."
            )

            st.subheader("Improved Response")

            st.markdown(
                escalation_result["output"]
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Escalated Model",
                escalation_result["escalated_model"]
            )

            col2.metric(
                "Additional Cost",
                f"${escalation_result['additional_cost']:.6f}"
            )

            col3.metric(
                "Total Cost",
                f"${escalation_result['total_cost']:.6f}"
            )

            del st.session_state[
                "escalation_request_id"
            ]

            if "escalation_message" in st.session_state:

                del st.session_state[
                    "escalation_message"
                ]

        else:

            st.error(
                escalation_result.get(
                    "message",
                    "Escalation failed."
                )
            )