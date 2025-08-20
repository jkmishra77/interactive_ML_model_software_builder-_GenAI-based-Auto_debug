import streamlit as st
from core.state import AgentState
from core.utils.logger import get_logger

logger = get_logger(__name__)

def model_feedback_node(state: AgentState) -> AgentState:
    try:
        st.subheader("🧠 Suggested Model Meta")
        st.code(state.model_meta, language="text")

        # Initialize session state for this node
        if "feedback_step" not in st.session_state:
            st.session_state.feedback_step = 1
        if "feedback_key" not in st.session_state:
            st.session_state.feedback_key = f"model_feedback_{st.session_state.get('session_id', 'default')}"

        # Step 1: Show feedback input
        if st.session_state.feedback_step == 1:
            feedback = st.text_input(
                "Enter '1' to agree or provide feedback to refine the model:",
                value=st.session_state.get(st.session_state.feedback_key, ""),
                key=st.session_state.feedback_key
            )

            # Step 2: Confirm feedback
            if feedback:
                if st.button("Next: Confirm Feedback", key="confirm_feedback_btn"):
                    st.session_state[st.session_state.feedback_key] = feedback
                    st.session_state.feedback_step = 2
                    logger.info(f"User feedback: {feedback}")
                    state.model_feedback = feedback

        # Step 2: Show confirmation
        elif st.session_state.feedback_step == 2:
            st.success("✅ Feedback confirmed.")
            st.write(f"Model Feedback: `{state.model_feedback}`")
            
            if st.button("Continue to Code Generation", key="continue_btn"):
                st.session_state.feedback_step = 3  # Move to next step

        return AgentState(
            goal=state.goal,
            model_meta=state.model_meta,
            model_feedback=state.model_feedback,
            code_feedback=state.code_feedback,
            generated_code=state.generated_code,
            instructions=state.instructions,
            execution_result=state.execution_result
        )

    except Exception as e:
        logger.error(f"Error in model_feedback_node: {e}")
        st.error("⚠️ Error during model feedback processing.")
        return state