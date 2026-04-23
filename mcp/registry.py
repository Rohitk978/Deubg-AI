"""
Tool registry — defines all available tools, their capabilities,
and keyword-based routing rules.

To add a new tool:
1. Add an entry to TOOLS dict
2. Add its keywords to KEYWORD_TOOL_MAP
"""

TOOLS = {
    "llm_solver": {
        "description": "Uses a local LLM to generate code fixes for detected bugs",
        "capabilities": [
            "Fix syntax errors",
            "Fix logic bugs",
            "Fix SQL injection vulnerabilities",
            "Fix missing error handling",
            "Replace unsafe patterns with safe alternatives",
        ],
        "best_for": ["syntax_error", "logic_bug", "crash", "security", "resource_leak"],
        "not_suitable_for": ["dependency_errors", "environment_setup", "unknown_libraries"],
    },

    "web_search": {
        "description": "Searches the web for documentation, error explanations, and library fixes",
        "capabilities": [
            "Find documentation for unknown libraries",
            "Look up error messages",
            "Find fix examples for dependency issues",
            "Search for API usage examples",
        ],
        "best_for": ["import_error", "dependency_error", "api_error", "unknown_library"],
        "not_suitable_for": ["pure_logic_bugs", "syntax_errors", "crashes"],
    },
}

# Keyword - tool routing map
# Used by router to pick the right tool based on analysis content
KEYWORD_TOOL_MAP = {
    #  llm_solver
    "syntax error": "llm_solver",
    "keyerror": "llm_solver",
    "typeerror": "llm_solver",
    "crash": "llm_solver",
    "sql injection": "llm_solver",
    "f-string": "llm_solver",
    "debug=true": "llm_solver",
    "resource leak": "llm_solver",
    "bare except": "llm_solver",
    "mutable default": "llm_solver",
    "hardcoded": "llm_solver",

    #  web_search
    "import error": "web_search",
    "modulenotfounderror": "web_search",
    "no module named": "web_search",
    "dependency": "web_search",
    "api error": "web_search",
    "connection error": "web_search",
}

def select_tool(analysis: str, user_mode: str = "llm_solver") -> str:
    """
    Select the best tool based on analysis content and user preference.
    User mode overrides keyword detection when explicitly set.
    """
    if user_mode in ("web_search", "llm_solver"):
        return user_mode

    lower = analysis.lower()
    for keyword, tool in KEYWORD_TOOL_MAP.items():
        if keyword in lower:
            return tool

    return "llm_solver"  
