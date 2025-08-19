# test_run.py

from agent import agent_executor
from agent.state import AgentState

def run_test():
    initial_state = AgentState(
        user_input="Build a pipeline for customer churn prediction",
        execution_logs=[]
    )

    final_state = agent_executor.invoke(initial_state)

    print("\n=== Final State ===")
    print(final_state.model_dump_json(indent=2))

if __name__ == "__main__":
    run_test()
