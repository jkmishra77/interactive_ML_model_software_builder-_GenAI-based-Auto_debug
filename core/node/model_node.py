from core.state import AgentState
from core.utils.logger import setup_logger

from core.utils.logger import get_logger   

logger = get_logger(__name__)

def model_feedback_node(state: AgentState) -> AgentState:
    try:
        print("\n Suggested Model Meta:")
        print(state.model_meta)
        feedback = input("Enter '1' to agree or provide feedback to refine the model: ").strip()
        logger.info(f"User feedback: {feedback}")
        return AgentState(
            goal=state.goal,
            model_meta=state.model_meta,
            model_feedback=feedback
        )
    except Exception as e:
        logger.error(f"Error in model_feedback_node: {e}")
        return state
