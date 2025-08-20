# backend.py

from langgraph.graph import StateGraph, END, START
from pydantic import BaseModel
import subprocess, tempfile, os, logging

# Logging setup
logging.basicConfig(level=logging.ERROR, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("AI_Software_Builder")
logger.setLevel(logging.ERROR)
logger.propagate = True

# Agent state
class AgentState(BaseModel):
    goal: str = ""
    model_meta: str = ""
    model_feedback: str = ""
    code_feedback: str = ""
    generated_code: str = ""
    instructions: str = ""
    execution_result: dict = {}

# Placeholder for LLM query
def query_llm(prompt: str, model: str = settings.LLM_MODEL) -> str:
    try:
        if not groq_client:
            return "Error: LLM client not initialized"
            
        response = groq_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content

# Node 1: Goal and model suggestion
def goal_and_model_handler(state: AgentState) -> AgentState:
    try:
        prompt = f"Suggest the most suitable code for goal: {state.goal} and feedback: {state.model_feedback}"
        model_meta = query_llm(prompt).strip()
        return state.copy(update={"model_meta": model_meta})
    except Exception as e:
        logger.error(f"goal_and_model_handler: {e}")
        return state

# Node 2: Model feedback
def model_feedback_node(state: AgentState) -> AgentState:
    return state  # Feedback handled in frontend

# Node 3: Code generation
def codegen_node(state: AgentState) -> AgentState:
    try:
        if state.code_feedback.strip():
            prompt = f"""Generate complete runnable code for: {state.goal}
Feedback: {state.code_feedback}
Previous code: {state.generated_code}
Use dummy data where needed. Comment out file reads."""
        else:
            prompt = f"""Generate code for goal: {state.goal}
Model Meta: {state.model_meta}
Use dummy data. Comment out file reads."""

        interim_code = query_llm(prompt).strip()
        processed_prompt = f"""Strip any preamble. Start from 'import'. Ensure code runs with dummy data.
Code:\n{interim_code}"""
        processed_code = query_llm(processed_prompt).strip()

        return state.copy(update={"generated_code": processed_code})
    except Exception as e:
        logger.error(f"codegen_node: {e}")
        return state

# Node 4: Code feedback
def code_feedback_node(state: AgentState) -> AgentState:
    try:
        if state.code_feedback.strip() == "1":
            prompt = f"Write instructions to run this code:\n{state.generated_code}"
            instructions = query_llm(prompt).strip()
            return state.copy(update={"instructions": instructions})
        return state
    except Exception as e:
        logger.error(f"code_feedback_node: {e}")
        return state

# Node 5: Run code
def run_code_subprocess(state: AgentState) -> AgentState:
    code = state.generated_code
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

    return state.copy(update={"execution_result": execution_result})

# Routers
def model_router(state: AgentState):
    return "codegen_node" if state.model_feedback.strip() == "1" else "goal_and_model_handler"

def codegen_router(state: AgentState):
    return "run_code_subprocess" if state.code_feedback.strip() == "1" else "codegen_node"

def run_code_router(state: AgentState):
    return "end" if state.execution_result.get("success", 0) == 1 else "codegen_node"

# Build graph
def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("goal_and_model_handler", goal_and_model_handler)
    builder.add_node("model_feedback", model_feedback_node)
    builder.add_node("codegen_node", codegen_node)
    builder.add_node("code_feedback_node", code_feedback_node)
    builder.add_node("run_code_subprocess", run_code_subprocess)

    builder.add_edge(START, "goal_and_model_handler")
    builder.add_edge("goal_and_model_handler", "model_feedback")
    builder.add_edge("codegen_node", "code_feedback_node")
    builder.add_conditional_edges("model_feedback", model_router, {
        "codegen_node": "codegen_node",
        "goal_and_model_handler": "goal_and_model_handler"
    })
    builder.add_conditional_edges("code_feedback_node", codegen_router, {
        "run_code_subprocess": "run_code_subprocess",
        "codegen_node": "codegen_node"
    })
    builder.add_conditional_edges("run_code_subprocess", run_code_router, {
        "end": END,
        "codegen_node": "codegen_node"
    })

    return builder.compile()
