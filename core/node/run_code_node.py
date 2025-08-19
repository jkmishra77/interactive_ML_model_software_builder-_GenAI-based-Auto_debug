from core.state import AgentState
import subprocess
import tempfile
import os
import logging

from core.utils.logger import get_logger   

logger = get_logger(__name__)

def run_code_subprocess(state: AgentState) -> AgentState:
    code = state.generated_code
    print("running this code in subprocess\n----------------", code)
    
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
    except Exception as e:
        execution_result = {
            "stdout": "",
            "stderr": str(e),
            "exit_code": -1,
            "success": 0
        }
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