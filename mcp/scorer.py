def score_tools(analysis,tools):
    """
    Intelligent scoring between:
    - llm_solver (default for code debugging)
    - web_search (for external knowledge)

    """

    analysis  = analysis.lower()

    is_syntax = "syntax" in analysis
    is_runtime = "runtime" in analysis
    is_logic = "logic" in analysis

    is_dependency = any(word in analysis for word in [
        "library", "module", "package", "dependency", "install", "import error"
    ])

    is_api = any(word in analysis for word in [
        "api", "http", "request", "response", "endpoint"
    ])

    is_unknown = any(word in analysis for word in [
        "unknown", "not found", "not defined"
    ])

    if is_syntax or is_runtime or is_logic:
        return "llm_solver"
    
    if is_dependency or is_api or is_unknown:
        return "Web_search"
    

    return "llm_solver"