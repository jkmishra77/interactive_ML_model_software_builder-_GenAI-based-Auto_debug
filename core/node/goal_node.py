import streamlit as st
from datetime import datetime
from core.state import AgentState
from llm.query import query_llm
from core.utils.logger import get_logger

logger = get_logger(__name__)

def goal_and_model_handler(state: AgentState) -> AgentState:
    try:
        st.subheader("🎯 Define Business Goal and Select Model")

        timestamp = datetime.now().strftime("%S%f")  # e.g., "42123456"
        goal_key = f"goal_input_{timestamp}"

        if not state.model_feedback:
            goal_input = st.text_input(
                "Describe your business goal:",
                value=st.session_state.get(goal_key, ""),
                key=goal_key
            )
            if goal_input:
                st.session_state[goal_key] = goal_input
                state.goal = goal_input

        goal_input = state.goal or st.session_state.get(goal_key, "")
        if goal_input:
            prompt = f"Suggest the most suitable code for goal: {goal_input} and {state.model_feedback}"
            model_meta = query_llm(prompt).strip()
            logger.info(f"Goal: {goal_input} → Model Meta: {model_meta}")
        else:
            model_meta = state.model_meta

        return AgentState(
            goal=goal_input,
            model_meta=model_meta,
            model_feedback=state.model_feedback,
            code_feedback=state.code_feedback,
            generated_code=state.generated_code,
            instructions=state.instructions,
            execution_result=state.execution_result
        )

    except Exception as e:
        logger.error(f"Error in goal_and_model_handler: {e}")
        st.error("⚠️ Error while processing goal and model selection.")
        return state
