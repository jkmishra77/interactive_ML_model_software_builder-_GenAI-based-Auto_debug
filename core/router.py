from typing import Literal

def model_router(state):
    """Route based on model feedback - proceed to codegen or loop back to goal handler"""
    return "codegen_node" if state.model_feedback.strip() == "1" else "goal_and_model_handler"

def codegen_router(state):
    """Route based on code feedback - proceed to execution or loop back to code generation"""
    return "run_code_subprocess" if state.code_feedback.strip() == "1" else "codegen_node"

def run_code_router(state) -> Literal["end", "codegen_node"]:
    """Route based on execution result - end if successful, loop back to codegen if failed"""
    success = state.execution_result.get("success", 0)
    return "end" if success == 1 else "codegen_node"