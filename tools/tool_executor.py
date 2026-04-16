from langchain_core.messages import AIMessage


def tool_executor(state):
    print("Running Tool Executor...")

    # old version called LLM here to "fix" code — produced empty output.
    # tool_executor's only job is routing. Actual fixing is done in fix_agent.
    # No LLM call here at all.

    tool     = state.get("selected_tool", "llm_solver")
    analysis = state.get("analysis", "")

    if not analysis or "no issues found" in analysis.lower():
        print("Tool Executor: No issues — passing to validator.")
        return {
            "tool_result":   "No issues found.",
            "tool_status":   "skipped",
            "next_agent":    "validator",
        }

    print(f"Tool Executor: bugs found, routing to validator. Tool={tool}")

    return {
        "tool_result":   analysis,
        "selected_tool": tool,
        "tool_status":   "success",
        "next_agent":    "validator",
    }