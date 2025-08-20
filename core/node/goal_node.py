import streamlit as st
from core.state import AgentState
from llm.query import query_llm
from core.utils.logger import get_logger

logger = get_logger(__name__)

def goal_and_model_handler(state: AgentState) -> AgentState:
    try:
        st.subheader("🎯 Define Business Goal and Select Model")

        # Initialize session state for this node
        if "goal_step" not in st.session_state:
            st.session_state.goal_step = 1
        if "goal_key" not in st.session_state:
            st.session_state.goal_key = f"goal_input_{st.session_state.get('session_id', 'default')}"
            st.stop()
        if "feedback_key" not in st.session_state:
            st.session_state.feedback_key = f"model_feedback_{st.session_state.get('session_id', 'default')}"

        # Step 1: Business Goal
        if st.session_state.goal_step == 1:
            goal_input = st.text_input(
                "Step 1: Describe your business goal", 
                key=st.session_state.goal_key
            )

            if goal_input and st.button("Next: Proceed to Model Feedback", key="goal_next_btn"):
                st.session_state.goal_step = 2
                state.goal = goal_input
                st.rerun()

        # Step 2: Model Feedback
        elif st.session_state.goal_step == 2:
            model_feedback = st.text_area(
                "Step 2: Provide model feedback", 
                key=st.session_state.feedback_key
            )

            if model_feedback and st.button("Next: Generate Model Suggestion", key="feedback_next_btn"):
                st.session_state.goal_step = 3
                state.model_feedback = model_feedback
                st.rerun()

        # Step 3: Model Suggestion
        elif st.session_state.goal_step == 3:
            if state.goal and state.model_feedback:
                with st.spinner("Generating model suggestion..."):
                    prompt = f"Suggest the most suitable code for goal: {state.goal} and {state.model_feedback}"
                    model_meta = query_llm(prompt).strip()
                    logger.info(f"Goal: {state.goal} → Model Meta: {model_meta}")
            else:
                model_meta = state.model_meta

            st.success("✅ Model suggestion generated.")
            st.code(model_meta, language="text")

            if st.button("Continue to Next Step", key="model_continue_btn"):
                st.session_state.goal_step = 4

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
        logger.error(f"Error in goal_and_model_handler: {e}")
        st.error("⚠️ Error while processing goal and model selection.")
        return state