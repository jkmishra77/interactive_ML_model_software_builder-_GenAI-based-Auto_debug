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

class AgentState(BaseModel):
    goal: str = ""
    model_meta: str = ""
    model_feedback: str = ""
    code_feedback: str = ""
    generated_code: str = ""
    instructions: str = ""
    execution_result: Dict = Field(default_factory=dict)

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
            prompt = f"""You are an expert python engineer,  Generate complete runnable  
            generate the code for {goal}  \n {code_feedback} \n  {previous_code}\n

Use a dummy dataset where needed.
Comment out only the line where data is read from file (e.g., df = pd.read_csv(...)).
Generate complete runnable code start from import library."""
        else:
            prompt = f"""Generate code as per user requirement:
{goal}\n 
Model Meta: {model_meta}
Use a dummy dataset or toy dataset where needed.
Comment out only the line where data is read from file (e.g., df = pd.read_csv(...)).
Ensure the rest of the code is runnable."""

        interim_code1 = query_llm(prompt).strip()
        
        prompt2= f''' you are a pythen expert. preprocess the code and provide runable code. 
        follw these rules  \n (1) strip the intial few line till import line till line start from import and process it : \n {interim_code1} \n\n 
        (2). dont include any mark like at begining like < ' , " , ```, etc > dont include any output line   like   <"```python", "Here is the code' , "python code">  \n
          (3) output shoul be code snippet  ensure code runable by capy paste in python file and run it. \n
          (4) no external librery is allowed to import '''
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
    """Node 5: run code in subprocess with automatic package installation"""
    try:
        # Package mapping: patterns -> package names
        pkg_map = {
            'import pandas': 'pandas', 'import numpy': 'numpy',
            'import sklearn': 'scikit-learn', 'import matplotlib': 'matplotlib',
            'import seaborn': 'seaborn', 'import tensorflow': 'tensorflow',
            'import torch': 'torch'
        }
        
        # Find packages to install
        packages_to_install = []
        for pattern, pkg_name in pkg_map.items():
            if pattern in code and pkg_name not in packages_to_install:
                packages_to_install.append(pkg_name)
        
        # Create temporary file with installation commands
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            # ADD INSTALLATION COMMANDS HERE
            if packages_to_install:
                f.write("import subprocess\nimport sys\n\n")
                f.write("# Installing required packages...\n")
                for pkg in packages_to_install:
                    f.write(f"subprocess.run([sys.executable, '-m', 'pip', 'install', '{pkg}'])\n")
                f.write("\n")
                f.write("# Package installation completed. Running code...\n")
                f.write("print('=' * 50)\n\n")
            
            # Add the original code
            f.write(code)
            path = f.name

        try:
            result = subprocess.run(["python", path], capture_output=True, text=True, timeout=60)
            execution_result = {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "success": 1 if result.returncode == 0 else 0,
                "packages_installed": packages_to_install  # Track what was installed
            }
        except Exception as e:
            execution_result = {
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1,
                "success": 0,
                "packages_installed": packages_to_install
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
            "success": 0,
            "packages_installed": []
        }