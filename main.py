from core.agent import AIBuilderAgent
import logging

# Global logging config
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# Suppress noisy third-party logs
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)

# Local module logger
logger = logging.getLogger("AI_Software_Builder")
logger.setLevel(logging.ERROR)
logger.propagate = True

if __name__ == "__main__":
    try:
        agent = AIBuilderAgent()
        final_state = agent.run()

        print('\n\n********************code****************:\n\n', final_state["generated_code"])
        print('\n\n********************Instructions***************:\n\n', final_state["instructions"])
        
    except Exception as e:
        logger.error(f"System error: {str(e)}")