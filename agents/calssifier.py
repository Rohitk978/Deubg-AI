from utils.llm import get_llm, extract_text
from config import LLM_PROVIDER
llm = get_llm(LLM_PROVIDER)


def classifier_agent(state):
    print("Running Classifier...")
    messages = state.get("messages", [])
    input = messages[-1] if messages else ""

    problem = (
        input.content
        if hasattr(input, "content")
        else str(input)
    )

    prompt = f"""
Classify this programming issue.

Possible categories:
- syntax_error
- runtime_error
- dependency_error
- logic_error

Problem:
{problem}

Return only the category.
"""
    
    response = llm.invoke(prompt)

    result = (
        response.content
        if hasattr(response, "content")
        else str(response)
    )

    error_type = result.strip()

    return {
        "error_type": error_type,
        "next_agent": "supervisor"
    }