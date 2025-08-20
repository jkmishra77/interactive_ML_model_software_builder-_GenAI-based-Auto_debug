import streamlit as st
from uuid import uuid4
from core.state import AgentState
from llm.query import query_llm
from core.utils.logger import get_logger

logger = get_logger(__name__)

def goal_and_model_handler(state: AgentState) -> AgentState:
    try:
        st.subheader("🎯 Define Business Goal and Select Model")

        # Initialize step tracker
        if "goal_step" not in st.session_state:
            st.session_state.goal_step = 1

        # Step 1: Business Goal
        if st.session_state.goal_step >= 1:
            goal_key = f"goal_input_{uuid4().hex}"
            goal_input = st.text_input("Step 1: Describe your business goal", key=goal_key)
            if goal_input and st.session_state.goal_step == 1:
                st.session_state.goal_step = 2
                state.goal = goal_input

        # Step 2: Model Feedback
        if st.session_state.goal_step >= 2:
            feedback_key = f"model_feedback_{uuid4().hex}"
            model_feedback = st.text_area("Step 2: Provide model feedback", key=feedback_key)
            if model_feedback and st.session_state.goal_step == 2:
                st.session_state.goal_step = 3
                state.model_feedback = model_feedback

        # Step 3: Model Suggestion
        goal_input = state.goal
        model_feedback = state.model_feedback
        if goal_input and model_feedback:
            prompt = f"Suggest the most suitable code for goal: {goal_input} and {model_feedback}"
            model_meta = query_llm(prompt).strip()
            logger.info(f"Goal: {goal_input} → Model Meta: {model_meta}")
        else:
            model_meta = state.model_meta

        return AgentState(
            goal=goal_input,
            model_meta=model_meta,
            model_feedback=model_feedback,
            code_feedback=state.code_feedback,
            generated_code=state.generated_code,
            instructions=state.instructions,
            execution_result=state.execution_result
        )

    except Exception as e:
        logger.error(f"Error in goal_and_model_handler: {e}")
        st.error("⚠️ Error while processing goal and model selection.")
        return state
