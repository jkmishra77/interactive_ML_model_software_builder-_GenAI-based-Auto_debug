import streamlit as st
from backend import (
    goal_and_model_handler, 
    codegen_node, 
    generate_instructions, 
    run_code_subprocess, 
    AgentState
)

st.set_page_config(page_title="AI Software Builder", layout="wide")
st.title("🚀 AI Software Builder")

# Initialize session state
if 'state' not in st.session_state:
    st.session_state.state = AgentState()
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1

state = st.session_state.state
current_step = st.session_state.current_step

# Step 1: Goal Input (Node 1)
if current_step == 1:
    st.subheader("🎯 Step 1: Define Your Goal")
    
    if not state.goal:
        goal = st.text_input("Welcome! Please describe your business goal:")
        if st.button("Submit Goal") and goal:
            state.goal = goal.strip()
            st.rerun()
    else:
        st.success(f"Goal set: {state.goal}")
        if st.button("Next →"):
            st.session_state.current_step = 2
            st.rerun()

# Step 2: Model Suggestion & Feedback (Nodes 1 + 2)
elif current_step == 2:
    st.subheader("🤖 Step 2: Model Suggestion")
    
    # Generate model suggestion (Node 1)
    if not state.model_meta:
        with st.spinner("Generating model suggestion..."):
            state.model_meta = goal_and_model_handler(state.goal, state.model_feedback)
    
    st.write("**Suggested Model Meta:**")
    st.code(state.model_meta, language="text")
    
    # Model feedback (Node 2)
    st.subheader("Provide Feedback")
    feedback = st.text_input("Enter '1' to agree or provide feedback to refine the model:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            st.session_state.current_step = 1
            st.rerun()
    with col2:
        if st.button("Next →") and feedback:
            state.model_feedback = feedback
            if feedback.strip() == "1":
                st.session_state.current_step = 3  # Approved → code generation
            else:
                st.session_state.current_step = 1  # Feedback → back to goal handler
            st.rerun()

# Step 3: Code Generation & Feedback (Nodes 3 + 4)
elif current_step == 3:
    st.subheader("💻 Step 3: Code Generation")
    
    # Generate code (Node 3)
    if not state.generated_code:
        with st.spinner("Generating code..."):
            state.generated_code = codegen_node(state.goal, state.model_meta, state.code_feedback, state.generated_code)
    
    st.write("**Generated Code:**")
    st.code(state.generated_code, language="python")
    
    # Code feedback (Node 4)
    st.subheader("Code Feedback")
    code_feedback = st.text_input("Enter '1' to accept the code or provide feedback to refine it:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            st.session_state.current_step = 2
            st.rerun()
    with col2:
        if st.button("Next →") and code_feedback:
            state.code_feedback = code_feedback
            if code_feedback.strip() == "1":
                # Generate instructions and proceed to execution
                with st.spinner("Generating instructions..."):
                    state.instructions = generate_instructions(state.generated_code)
                st.session_state.current_step = 4
            else:
                # Feedback → regenerate code
                state.generated_code = ""
            st.rerun()

# Step 4: Execution & Results (Nodes 4 + 5)
elif current_step == 4:
    st.subheader("⚡ Step 4: Execution")
    
    # Show instructions (Node 4)
    if state.instructions:
        st.write("**Instructions to Run:**")
        st.write(state.instructions)
    
    # Execute code (Node 5)
    if not state.execution_result:
        with st.spinner("Running code..."):
            state.execution_result = run_code_subprocess(state.generated_code)
    
    st.write("**Execution Results:**")
    if state.execution_result.get("stdout"):
        st.success("✅ Output:")
        st.code(state.execution_result["stdout"])
    if state.execution_result.get("stderr"):
        st.error("❌ Errors:")
        st.code(state.execution_result["stderr"])
    
    # --- NEW LOGIC STARTS HERE ---
    # Handle execution result routing based on success/failure
    if state.execution_result.get("success") == 1:
        st.success("🎉 Execution successful!")
        
        # Present the user with a choice after successful execution
        st.write("**What would you like to do next?**")
        
        col_modify, col_finish = st.columns(2)
        with col_modify:
            if st.button("🔄 Modify Code"):
                # Set feedback to trigger code regeneration and go back to Step 3
                state.code_feedback = "The code ran successfully. Please modify it as follows:"
                st.session_state.current_step = 3
                st.rerun()
        with col_finish:
            if st.button("🏁 END"):
                # Reset the entire session
                st.session_state.state = AgentState()
                st.session_state.current_step = 1
                st.rerun()
                
    else:
        st.warning("⚠️ Execution failed.")
        
        # On failure, the options are "Retry" (go back to code gen) or "END"
        col_retry, col_finish = st.columns(2)
        with col_retry:
            if st.button("🔄 Retry Code Generation"):
                # Clear the code and result to trigger regeneration
                state.generated_code = ""
                state.execution_result = {}
                st.session_state.current_step = 3
                st.rerun()
        with col_finish:
            if st.button("🏁 END"):
                st.session_state.state = AgentState()
                st.session_state.current_step = 1
                st.rerun()
    # --- NEW LOGIC ENDS HERE ---
# Progress sidebar
st.sidebar.subheader("Workflow Progress")
steps = [
    ("1. Goal Input", current_step >= 1),
    ("2. Model Feedback", current_step >= 2), 
    ("3. Code Generation", current_step >= 3),
    ("4. Execution", current_step >= 4)
]

for step_name, completed in steps:
    status = "✅" if completed else "⏳"
    st.sidebar.write(f"{status} {step_name}")