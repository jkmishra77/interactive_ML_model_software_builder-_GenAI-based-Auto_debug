import streamlit as st
from datetime import datetime
from core.state import AgentState
from core.utils.logger import get_logger

logger = get_logger(__name__)

def model_feedback_node(state: AgentState) -> AgentState:
    try:
        st.subheader("🧠 Suggested Model Meta")
        st.code(state.model_meta, language="text")

        timestamp = datetime.now().strftime("%S%f")  # e.g., "42123456"
        feedback_key = f"model_feedback_{timestamp}"

        feedback = st.text_input(
            "Enter '1' to agree or provide feedback to refine the model:",
            value=st.session_state.get(feedback_key, ""),
            key=feedback_key
        )

        if feedback:
            st.session_state[feedback_key] = feedback
            logger.info(f"User feedback: {feedback}")

        return AgentState(
            goal=state.goal,
            model_meta=state.model_meta,
            model_feedback=st.session_state.get(feedback_key, "")
        )

    except Exception as e:
        logger.error(f"Error in model_feedback_node: {e}")
        st.error("⚠️ Error during model feedback processing.")
        return state
