from typing import List, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage


class DebugState(TypedDict, total=False):
    """
    total=False  ->  every key is optional so LangGraph can do partial updates.
    Each agent returns only the keys it changes; LangGraph merges them.
    """

    # conversation history
    messages: List[BaseMessage]

    # code payloads
    code: str   
    fixed_code: str   
    language: str

    # agent communication
    analysis: str   
    selected_tool: str
    tool_result: str
    output: str

    # routing: MUST be a plain str, never a list
    next_agent: str

    # execution state
    execution_status: str  
    iteration: int

    # loop-breaker
    fix_attempts: int   
    max_fix_attempts: int   
