import streamlit as st
from datetime import datetime
from core.state import AgentState
from llm.query import query_llm
from core.utils.logger import get_logger

logger = get_logger(__name__)

def codegen_node(state: AgentState) -> AgentState:
    try:
        st.subheader("⚙️ Code Generation Node")

        if state.code_feedback.strip():
            prompt = f"""You are an expert python engineer. Generate complete runnable code starting from import statements.
Generate the code for: {state.goal}  
User feedback: {state.code_feedback}  
Previous code: {state.generated_code}

Use a dummy dataset where needed.
Comment out only the line where data is read from file (e.g., df = pd.read_csv(...)).
"""
        else:
            prompt = f"""Generate code as per user goal:
{state.goal}  
Model Meta: {state.model_meta}

Use a dummy dataset where needed.
Comment out only the line where data is read from file (e.g., df = pd.read_csv(...)).
Ensure the rest of the code is runnable.
"""

        interim_code1 = query_llm(prompt).strip()

        prompt2 = f"""If the code requires data from user, provide some toy data to run the code without any intervention. 
Strip the initial few lines till import line is reached and give the code for:\n{interim_code1}

Don't include any quotes or reply lines. Start directly from import.
"""
        processed_code = query_llm(prompt2).strip()

        timestamp = datetime.now().strftime("%S%f")  # e.g., "42123456"
        code_key = f"generated_code_{timestamp}"

        st.success("✅ Code generated successfully.")
        st.code(processed_code, language="python", key=code_key)

        return AgentState(
            goal=state.goal,
            model_meta=state.model_meta,
            model_feedback=state.model_feedback,
            code_feedback=state.code_feedback,
            generated_code=processed_code,
            instructions=state.instructions,
            execution_result=state.execution_result
        )

    except Exception as e:
        logger.error(f"Error in codegen_node: {e}")
        st.error("⚠️ Error during code generation.")
        return state
