from utils.llm import generate_response, extract_text
from langchain_core.messages import AIMessage


def explainer_agent(state):
    print("Running Explainer Agent...")

    analysis   = state.get("analysis", "")
    fixed_code = state.get("fixed_code", "") or state.get("code", "")
    language   = state.get("language", "code")
    messages   = state.get("messages", [])

    no_bugs = (
        not analysis
        or "no issues found" in analysis.lower()
        or "no valid issues" in analysis.lower()
    )

    if no_bugs:
        explanation = f"""## ✅ No Bugs Found

Your {language} code is correct. No issues were detected.

### Your Code
```{language}
{fixed_code}
```"""
        return {
            "final_answer": explanation,
            "output":       explanation,
            "messages":     messages + [AIMessage(content=explanation)],
            "next_agent":   "reflection_agent",
        }

    prompt = f"""You are a senior software engineer doing a detailed code review.

Bugs found in this {language} code:
{analysis}

Corrected code:
{fixed_code}

For EACH bug write a full detailed explanation using this format:

---
### Bug N — <bug name> (<line location>)

**What is wrong:**
Write a full detailed explanation of what the bug is, what the problematic code does,
and what behaviour it causes. Do not be brief — explain it thoroughly so a junior
developer can fully understand the problem.

**Why it breaks at runtime:**
Explain in detail exactly what happens when this bug is triggered. What error is thrown,
what data is lost, what security risk is exposed, or what wrong result is produced.
Give a concrete example of how it fails (e.g. what input causes the crash).

**Step-by-step solution:**
1. <Detailed first step — explain what to do and why>
2. <Detailed second step — explain what to do and why>
3. <Continue until the fix is fully explained>

After covering ALL bugs write:

---
### ✅ Corrected Code
```{language}
<paste the complete corrected code here>
```

Important rules:
- Never write one-liner explanations — always write full paragraphs
- Every step in the solution must explain both WHAT to do and WHY
- Cover every single bug in the list, do not skip any
- Always finish with the complete corrected code block"""

    response    = generate_response(prompt)
    explanation = extract_text(response)

    # if model returns empty, show raw analysis + fixed code
    if not explanation or len(explanation.strip()) < 30:
        explanation = f"""## 🔍 Code Analysis Report

### Bugs Found
{analysis}

### ✅ Corrected Code
```{language}
{fixed_code}
```"""

    return {
        "final_answer": explanation,
        "output":       explanation,
        "messages":     messages + [AIMessage(content=explanation)],
        "next_agent":   "reflection_agent",
    }