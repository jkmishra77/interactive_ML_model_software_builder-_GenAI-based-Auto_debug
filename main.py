import streamlit as st
import logging
from core.agent import AIBuilderAgent

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

# Streamlit UI
st.title("🧠 AI Software Builder")

if "final_state" not in st.session_state:
    st.session_state.final_state = None

if st.button("🚀 Run Agent Workflow"):
    try:
        agent = AIBuilderAgent()
        final_state = agent.run()
        st.session_state.final_state = final_state
        st.success("✅ Agent workflow completed.")
    except Exception as e:
        logger.error(f"System error: {str(e)}")
        st.error("❌ Agent execution failed.")

# Display results
if st.session_state.final_state:
    st.subheader("🧾 Generated Code")
    st.code(st.session_state.final_state.generated_code, language="python")

    st.subheader("📋 Instructions")
    st.text_area("Instructions", st.session_state.final_state.instructions or "No instructions generated.", height=150)
