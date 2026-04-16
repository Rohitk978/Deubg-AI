from langchain_core.messages import AIMessage


def reflection_agent(state):
    print("Running Reflection...")

    solution = state.get("final_answer", "")
    fixed_code = state.get("fixed_code", "") or state.get("code", "")
    messages = state.get("messages", [])

    if not solution or len(solution.strip()) < 20:
        fallback = f" Analysis Complete\n\nFinal Code\n\n{fixed_code}\n"
        return {
            "output":     fallback,
            "next_agent": "__end__",
        }

    print("Reflection: passing final answer through unchanged.")
    return {
        "output":     solution,   
        "next_agent": "__end__",
    }
