import streamlit as st
from core.agent import graph, AgentState

st.title("🧠 AI Software Builder")

# Step 1: Goal input
goal = st.text_input("Describe your business goal")
if goal:
    initial_state = AgentState(goal=goal)
    state = graph.invoke(initial_state)

    # Step 2: Show model suggestion
    st.subheader("Suggested Model Meta")
    st.markdown(state.model_meta)

    feedback = st.text_input("Enter '1' to accept or refine the model")
    if feedback:
        state.model_feedback = feedback
        state = graph.invoke(state)

        # Step 3: Show generated code
        st.subheader("Generated Code")
        st.code(state.generated_code, language="python")

        code_feedback = st.text_input("Enter '1' to accept or refine the code")
        if code_feedback:
            state.code_feedback = code_feedback
            state = graph.invoke(state)

            # Step 4: Show instructions
            if state.instructions:
                st.subheader("Instructions to Run")
                st.markdown(state.instructions)

            # Step 5: Show execution result
            st.subheader("Execution Result")
            st.text("Stdout:")
            st.code(state.execution_result.get("stdout", ""))
            st.text("Stderr:")
            st.code(state.execution_result.get("stderr", ""))
