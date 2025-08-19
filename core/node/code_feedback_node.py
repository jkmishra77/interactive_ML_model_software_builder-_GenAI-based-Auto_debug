from core.state import AgentState
from llm.query import query_llm
import logging

from core.utils.logger import get_logger  

logger = get_logger(__name__)


def code_feedback_node(state: AgentState) -> AgentState:
    try:
        instructions = ""
        feedback = input("Enter '1' to accept the code or provide feedback to refine it: ").strip()
        logger.info(f"Code feedback: {feedback}")
        
        if feedback == '1':
            prompt = f'''write the instructions to run this code:\n{state.generated_code}'''
            instructions = query_llm(prompt).strip()
        
         
        return AgentState(
            goal=state.goal,
            model_meta=state.model_meta,
            model_feedback=state.model_feedback,
            execution_result=state.execution_result,
            generated_code=state.generated_code,
            instructions=instructions,
            code_feedback=feedback
        )
    
    except Exception as e:
        logger.error(f"Error in code_feedback_node: {e}")
        return state