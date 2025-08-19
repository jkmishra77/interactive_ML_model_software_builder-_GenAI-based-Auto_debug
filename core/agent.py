from langgraph.graph import StateGraph, END, START  
from core.state import AgentState
from core.node import (
    goal_and_model_handler,
    model_feedback_node,
    codegen_node,
    code_feedback_node,
    run_code_subprocess
)
from core.router import model_router, codegen_router, run_code_router
import logging

logger = logging.getLogger("AI_Software_Builder")

class AIBuilderAgent:
    def __init__(self):
        self.workflow = StateGraph(AgentState)
        self._build_workflow()

    def _build_workflow(self):
        # Add nodes
        self.workflow.add_node("goal_and_model_handler", goal_and_model_handler)
        self.workflow.add_node("model_feedback", model_feedback_node)
        self.workflow.add_node("codegen_node", codegen_node)
        self.workflow.add_node("code_feedback_node", code_feedback_node)
        self.workflow.add_node("run_code_subprocess", run_code_subprocess)

        # Add edges
        self.workflow.add_edge(START, "goal_and_model_handler")  # ✅ Now START is defined
        self.workflow.add_edge("goal_and_model_handler", "model_feedback")
        self.workflow.add_edge("codegen_node", "code_feedback_node")

        # Add conditional edges
        self.workflow.add_conditional_edges(
            "model_feedback", 
            model_router, 
            {"codegen_node": "codegen_node", "goal_and_model_handler": "goal_and_model_handler"}
        )

        self.workflow.add_conditional_edges(
            "code_feedback_node", 
            codegen_router, 
            {"run_code_subprocess": "run_code_subprocess", "codegen_node": "codegen_node"}
        )

        self.workflow.add_conditional_edges(
            "run_code_subprocess", 
            run_code_router, 
            {"end": END, "codegen_node": "codegen_node"}  
        )

    def run(self):
        return self.workflow.compile().invoke(AgentState())