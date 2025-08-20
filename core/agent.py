import streamlit as st
import logging
from langgraph.graph import StateGraph, END, START  
from core.state import AgentState
from core.node import (
    goal_and_model_handler_streamlit,
    model_feedback_node_streamlit,
    codegen_node_streamlit,
    code_feedback_node_streamlit,
    run_code_subprocess_streamlit
)
from core.router import model_router, codegen_router, run_code_router
from core.utils.logger import get_logger

logger = get_logger("AI_Software_Builder")

class AIBuilderAgent:
    def __init__(self):
        self.workflow = StateGraph(AgentState)
        self._build_workflow()

    def _build_workflow(self):
        # Add Streamlit-compatible nodes
        self.workflow.add_node("goal_and_model_handler", goal_and_model_handler_streamlit)
        self.workflow.add_node("model_feedback", model_feedback_node_streamlit)
        self.workflow.add_node("codegen_node", codegen_node_streamlit)
        self.workflow.add_node("code_feedback_node", code_feedback_node_streamlit)
        self.workflow.add_node("run_code_subprocess", run_code_subprocess_streamlit)

        # Add edges
        self.workflow.add_edge(START, "goal_and_model_handler")
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

    def run(self, initial_state: AgentState = None):
        if initial_state is None:
            initial_state = AgentState()
        return self.workflow.compile().invoke(initial_state)
