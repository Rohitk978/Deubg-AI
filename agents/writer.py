from utils.llm import get_llm, extract_text
from config import LLM_PROVIDER
from langchain_core.messages import AIMessage

llm = get_llm(LLM_PROVIDER)

def writer_agent(state):
    print("Running Writer...")

    messages = state.get("messages", [])
    input = messages[-1] if messages else ""

    problem = (
        input.content
        if hasattr(input, "content")
        else str(input)
    )

    analysis = state.get("analysis", "")
    lang = state.get("language", "unknown")
    tool_result = state.get("tool_result", "")

    prompt = f"""
You are a backend debugging assistant.

Your ONLY job is to FIX the given code based on VERIFIED issues.

=====================
STRICT RULES (MANDATORY)
=====================

1. DO NOT analyze the code again
2. DO NOT add new issues
3. DO NOT change architecture
4. DO NOT remove Flask routes
5. DO NOT create new functions
6. ONLY fix the issues provided
7. Keep changes MINIMAL and LOCAL
8. Preserve original structure and logic

If you modify unrelated parts → output is WRONG

=====================
INPUT CODE
=====================
{problem}

=====================
VERIFIED ISSUES
=====================
{analysis}

=====================
OUTPUT FORMAT (STRICT)
=====================

### Fix Explanation (Step-by-step)

Fix 1:
- What was wrong
- What was changed

Fix 2:
...

### Corrected Code (FULL)

<only corrected version of original code>

"""
    
    response = llm.invoke(prompt)

    answer = (
        response.content
        if hasattr(response, "content")
        else str(response)
    )

    if "Fixed Code" not in answer and tool_result:
        answer += "\n\n### Fixed Code\n"
        answer += tool_result

    return {
        "final_answer": answer,
        "messages": [AIMessage(content=answer)],
        "next_agent": "__end__"
    }