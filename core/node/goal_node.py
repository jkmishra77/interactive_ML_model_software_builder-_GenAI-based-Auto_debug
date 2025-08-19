from core.state import AgentState
from llm.query import query_llm
from core.utils.logger import get_logger  

logger = get_logger(__name__)

def goal_and_model_handler(state: AgentState) -> AgentState:
    try:
        if not state.model_feedback:
            goal_input = ""
            print(" Welcome! Please describe your business goal:")
            goal_input = input("Goal: ").strip()
            state.goal = goal_input
        
        goal_input = state.goal   
        prompt = f"Suggest the most suitable code for goal: {state.goal} and {state.model_feedback}"
        model_meta = query_llm(prompt).strip()

        logger.info(f"Goal: {goal_input} → Model Meta: {model_meta}")
        
         
        return AgentState(
            goal=goal_input,
            model_meta=model_meta,
            model_feedback=state.model_feedback,
            code_feedback=state.code_feedback,
            generated_code=state.generated_code,
            instructions=state.instructions,
            execution_result=state.execution_result
        )

    except Exception as e:
        logger.error(f"Error in goal_and_model_handler: {e}")
         
        return AgentState(
            goal=state.goal,
            model_meta=state.model_meta,
            model_feedback=state.model_feedback,
            code_feedback=state.code_feedback,
            generated_code=state.generated_code,
            instructions=state.instructions,
            execution_result=state.execution_result
        )