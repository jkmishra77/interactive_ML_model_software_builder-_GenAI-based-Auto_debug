# core/diagnostics/import_check.py
import importlib

node_modules = [
    "goal_node",
    "model_feedback_node",
    "data_validation_node",
    "tool_router_node",
    "final_output_node",
    # Add all expected node modules here
]

for mod in node_modules:
    try:
        importlib.import_module(f"core.node.{mod}")
        print(f"[✓] core.node.{mod} imported successfully")
    except Exception as e:
        print(f"[✗] core.node.{mod} failed: {type(e).__name__} - {e}")
