from groq import Groq
from core.configs.settings import settings
import logging

from core.utils.logger import get_logger  # FIXED

logger = get_logger(__name__)

# Initialize Groq client
try:
    groq_client = Groq(api_key=settings.GROQ_API_KEY)
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    groq_client = None

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
    except Exception as e:
        logger.error(f"LLM query failed: {e}")
        return f"Error: {str(e)}"