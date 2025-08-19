from core.state import AgentState
from llm.query import query_llm
import logging

from core.utils.logger import get_logger   

logger = get_logger(__name__)

def codegen_node(state: AgentState) -> AgentState:
    try:
        print("\n Generating code ")

        if state.code_feedback.strip():
            prompt = f"""You are an expert python engineer Generate complete runnable code start from import library, 
            generate the code for {state.goal}  \n {state.code_feedback} \n  {state.generated_code }\n

Use a dummy dataset where needed.
Comment out only the line where data is read from file (e.g., df = pd.read_csv(...)).
Generate complete runnable code start from import library.
"""
        else:
            prompt = f"""Generate code as per user goal:
{state.goal}\n 
Model Meta: {state.model_meta}
Use a dummy dataset where needed.
Comment out only the line where data is read from file (e.g., df = pd.read_csv(...)).
Ensure the rest of the code is runnable."""

        interim_code1 = query_llm(prompt).strip()
        
        prompt2 = f'''If the code requires data from user, provide some toy data to run the code without any intervention. 
        Strip the initial few lines till import line is reached and give the code for {interim_code1}. 
        Don't include any mark like quotes, don't include any reply line like "Here is the code with the initial lines stripped till the import line:" etc. Start from import.'''
        
        processed_code = query_llm(prompt2).strip()
        
        print('processed_code', processed_code)

         
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
        return state