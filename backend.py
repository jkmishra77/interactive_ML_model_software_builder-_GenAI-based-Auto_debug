from groq import Groq
from pydantic import BaseModel, Field
import subprocess
import tempfile
import os
import logging
from typing import Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("AI_Software_Builder")

# Configuration
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "llama-3.3-70b-versatile")



# Initialize Groq client
try:
    groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
except Exception as e:
    logger.error(f"Groq init failed: {e}")
    groq_client = None

def query_llm(prompt: str) -> str:
    """Query the LLM with proper error handling"""
    try:
        if not groq_client:
            return "Error: LLM client not initialized"
        
        response = groq_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM query failed: {e}")
        return f"Error: {str(e)}"

def goal_and_model_handler(goal: str, model_feedback: str = "") -> str:
    """Node 1: Collect goal and suggest model - ORIGINAL PROMPT"""
    try:
        prompt = f"Suggest the most suitable code for goal: {goal} and {model_feedback}"
        model_meta = query_llm(prompt).strip()
        return model_meta
    except Exception as e:
        logger.error(f"Error in goal_and_model_handler: {e}")
        return f"Error: {str(e)}"

def codegen_node(goal: str, model_meta: str, code_feedback: str = "", previous_code: str = "") -> str:
    """Node 3: Code generation by LLM - ORIGINAL PROMPT"""
    try:
        if code_feedback.strip():
            prompt = f"""You are an expert python engineer Generate complete runnable code start from import library, 
            generate the code for {goal}  \n {code_feedback} \n  {previous_code}\n

Use a dummy dataset where needed.
Comment out only the line where data is read from file (e.g., df = pd.read_csv(...)).
Generate complete runnable code start from import library."""
        else:
            prompt = f"""Generate code as per user goal:
{goal}\n 
Model Meta: {model_meta}
Use a dummy dataset where needed.
Comment out only the line where data is read from file (e.g., df = pd.read_csv(...)).
Ensure the rest of the code is runnable."""

        interim_code1 = query_llm(prompt).strip()
        
        prompt2 = f'''if the code required data from user, you provide some toy data to run the code without any intervention. strip the initial few line till import line reach and give the code for {interim_code1}. 
        dont include any mark like ''' ''' at start and end dont include any reply line like <Here is the code with the initial lines stripped till the import line:> give the clean code only so taht it can be run by copy paste. final instruction output must be like
        example 1
        nothing should be here like this is you python code, pyhon code is here etc
        nothing should be here like '''  '''  """  """
        import pandas as pd
        import numpy as np
        main body here


        
        '''
        
        processed_code = query_llm(prompt2).strip()
        return processed_code

    except Exception as e:
        logger.error(f"Error in codegen_node: {e}")
        return f"Error: {str(e)}"

def generate_instructions(code: str) -> str:
    """Node 4: Code feedback - instructions part - ORIGINAL PROMPT"""
    try:
        prompt = f'''write the instructions to run this code:\n{code}'''
        instructions = query_llm(prompt).strip()
        return instructions
    except Exception as e:
        logger.error(f"Error generating instructions: {e}")
        return f"Error: {str(e)}"

def run_code_subprocess(code: str) -> Dict:
    """Node 5: run code in subprocess - ORIGINAL LOGIC"""
    try:
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
        
        return execution_result

    except Exception as e:
        logger.error(f"Error in run_code_subprocess: {e}")
        return {
            "stdout": "",
            "stderr": str(e),
            "exit_code": -1,
            "success": 0
        }