from pydantic import BaseModel
from typing import Optional, Dict

class AgentState(BaseModel):
    goal: str = ""
    model_meta: str = ""
    model_feedback: str = ""
    code_feedback: str = ""
    generated_code: str = ""
    instructions: str = ""
    execution_result: Dict = {}