from langchain_core.messages import AIMessage


def mcp_router(state):
    print("Running Router...")

    selected_tool = state.get("selected_tool", "llm_solver")

    if not selected_tool:
        selected_tool = "llm_solver"

    print(f"Router: using tool: {selected_tool}")

    return {
        "selected_tool": selected_tool,
        "next_agent": "tool_executor",
    }
