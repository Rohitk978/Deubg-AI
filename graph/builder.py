from langgraph.graph import StateGraph, END

from graph.state import DebugState
from agents.analyzer import analyzer_agent
from agents.validator import validator_agent
from agents.fix_agent import fix_agent
from agents.execution_agent import execution_agent
from agents.explainer_agent import explainer_agent
from agents.reflection_agent import reflection_agent
from tools.tool_executor import tool_executor
from mcp.router import mcp_router


def build_graph(state):
    print("Correct build_graph called")

    workflow = StateGraph(DebugState)

    workflow.add_node("analyzer",analyzer_agent)
    workflow.add_node("router",mcp_router)
    workflow.add_node("tool_executor",tool_executor)
    workflow.add_node("validator", validator_agent)
    workflow.add_node("fix_agent",fix_agent)
    workflow.add_node("execution_agent",execution_agent)
    workflow.add_node("explainer_agent",explainer_agent)
    workflow.add_node("reflection_agent",reflection_agent)

    workflow.set_entry_point("analyzer")

    workflow.add_conditional_edges(
        "analyzer", lambda s: s.get("next_agent", "__end__"),
        {"router": "router", "fix_agent": "fix_agent", "__end__": END}
    )
    

    workflow.add_conditional_edges(
        "router", lambda s: s.get("next_agent", "__end__"),
        {"tool_executor": "tool_executor", "fix_agent": "fix_agent", "__end__": END}
    )

    workflow.add_conditional_edges(
        "tool_executor", lambda s: s.get("next_agent", "__end__"),
        {"validator": "validator", "fix_agent": "fix_agent", "__end__": END}
    )

    #  validator must route to "fix_agent" 
    workflow.add_conditional_edges(
        
        "validator", lambda s: s.get("next_agent", "__end__"),
        {
            "fix_agent":       "fix_agent",        
            "execution_agent": "execution_agent",  
            "__end__": END,
            
        })

    #  fix_agent must route to "execution_agent" after fixing,
    workflow.add_conditional_edges(
        
        "fix_agent", lambda s: s.get("next_agent", "__end__"),
        {
            "execution_agent": "execution_agent", 
            "tool_executor":   "tool_executor",    
            "__end__": END,
            
        })

    workflow.add_conditional_edges(
        
        "execution_agent", lambda s: s.get("next_agent", "__end__"),
        {
            "explainer_agent": "explainer_agent",
            "fix_agent":       "fix_agent",
            "__end__": END,
            
        })

    # explainer returns next_agent="reflection_agent" but old builder
    workflow.add_conditional_edges(
        
        "explainer_agent", lambda s: s.get("next_agent", "__end__"),
        {
            "reflection_agent": "reflection_agent",  
            "__end__": END,
            
        })

    workflow.add_edge("reflection_agent", END)

    return workflow.compile()
