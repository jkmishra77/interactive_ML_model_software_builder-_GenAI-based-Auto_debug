import streamlit as st
from uuid import uuid4
from core.state import AgentState
from core.utils.logger import get_logger

logger = get_logger(__name__)

def model_feedback_node(state: AgentState) -> AgentState:
    try:
        st.subheader("🧠 Suggested Model Meta")
        st.code(state.model_meta, language="text")

        # Initialize step tracker
        if "feedback_step" not in st.session_state:
            st.session_state.feedback_step = 1

        # Step 1: Confirm model meta visibility
        if st.session_state.feedback_step == 1:
            if st.button("Proceed to Feedback"):
                st.session_state.feedback_step = 2

        # Step 2: Feedback Form
        if st.session_state.feedback_step >= 2:
            feedback_key = f"model_feedback_{uuid4().hex}"
            with st.form(key=f"model_feedback_form_{uuid4().hex}"):
                feedback = st.text_input(
                    "Enter '1' to agree or provide feedback to refine the model:",
                    value=st.session_state.get(feedback_key, ""),
                    key=feedback_key
                )
                submitted = st.form_submit_button("Submit Feedback")

            if submitted:
                st.session_state[feedback_key] = feedback
                logger.info(f"User feedback: {feedback}")
                st.session_state.feedback_step = 3  # Optional: advance to next node

        return AgentState(
            goal=state.goal,
            model_meta=state.model_meta,
            model_feedback=st.session_state.get(feedback_key, "")
        )

    except Exception as e:
        logger.error(f"Error in model_feedback_node: {e}")
        st.error("⚠️ Error during model feedback processing.")
        return state
