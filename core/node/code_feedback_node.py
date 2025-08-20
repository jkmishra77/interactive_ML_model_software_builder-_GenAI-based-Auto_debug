import streamlit as st
from core.state import AgentState
from llm.query import query_llm
from core.utils.logger import get_logger  

logger = get_logger(__name__)

def code_feedback_node(state: AgentState) -> AgentState:
    try:
        instructions = ""
        feedback_key = "code_feedback"

        with st.form("code_feedback_form"):
            st.subheader("🧪 Review Generated Code")
            st.code(state.generated_code, language="python")

            feedback = st.text_input(
                "Enter '1' to accept the code or provide feedback to refine it:",
                value=st.session_state.get(feedback_key, "")
            )
            submitted = st.form_submit_button("Submit Feedback")

        if submitted:
            st.session_state[feedback_key] = feedback
            logger.info(f"Code feedback: {feedback}")

            if feedback.strip() == '1':
                prompt = f'''write the instructions to run this code:\n{state.generated_code}'''
                instructions = query_llm(prompt).strip()

        return AgentState(
            goal=state.goal,
            model_meta=state.model_meta,
            model_feedback=state.model_feedback,
            execution_result=state.execution_result,
            generated_code=state.generated_code,
            instructions=instructions,
            code_feedback=st.session_state.get(feedback_key, "")
        )

    except Exception as e:
        logger.error(f"Error in code_feedback_node_streamlit: {e}")
        st.error("⚠️ Error during code feedback processing.")
        return state
