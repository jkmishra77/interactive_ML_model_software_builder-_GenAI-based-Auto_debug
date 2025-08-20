import streamlit as st
from core.state import AgentState
from core.utils.logger import get_logger

logger = get_logger(__name__)

def model_feedback_node(state: AgentState) -> AgentState:
    try:
        st.subheader("🧠 Suggested Model Meta")
        st.code(state.model_meta, language="text")

        feedback_key = "model_feedback"
        with st.form("model_feedback_form"):
            feedback = st.text_input(
                "Enter '1' to agree or provide feedback to refine the model:",
                value=st.session_state.get(feedback_key, "")
            )
            submitted = st.form_submit_button("Submit Feedback")

        if submitted:
            st.session_state[feedback_key] = feedback
            logger.info(f"User feedback: {feedback}")

        return AgentState(
            goal=state.goal,
            model_meta=state.model_meta,
            model_feedback=st.session_state.get(feedback_key, "")
        )

    except Exception as e:
        logger.error(f"Error in model_feedback_node_streamlit: {e}")
        st.error("⚠️ Error during model feedback processing.")
        return state
