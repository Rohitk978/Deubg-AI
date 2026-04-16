from langgraph.graph import END

def router(state):
    print("Running router")
    next_agent = state.get("next_agent")

    if next_agent == "__end__":
        return END
    
    return next_agent