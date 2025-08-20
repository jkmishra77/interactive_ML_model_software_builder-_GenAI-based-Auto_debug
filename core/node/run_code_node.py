import streamlit as st
import subprocess
import tempfile
import os
from core.state import AgentState
from core.utils.logger import get_logger

logger = get_logger(__name__)

def run_code_subprocess(state: AgentState) -> AgentState:
    code = state.generated_code
    st.subheader("🚀 Running Generated Code")
    st.code(code, language="python")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        path = f.name

    try:
        result = subprocess.run(["python", path], capture_output=True, text=True)
        execution_result = {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "success": 1
        }
        st.success("✅ Code executed successfully.")
        st.text_area("📤 Standard Output", result.stdout, height=200)
        if result.stderr:
            st.text_area("⚠️ Standard Error", result.stderr, height=200)
    except Exception as e:
        execution_result = {
            "stdout": "",
            "stderr": str(e),
            "exit_code": -1,
            "success": 0
        }
        st.error("❌ Error during code execution.")
        st.text_area("⚠️ Exception", str(e), height=200)
    finally:
        os.remove(path)

    return AgentState(
        execution_result=execution_result,
        goal=state.goal,
        model_meta=state.model_meta,
        model_feedback=state.model_feedback,
        generated_code=state.generated_code,
        instructions=state.instructions,
        code_feedback=state.code_feedback
    )
