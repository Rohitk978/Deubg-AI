import re
from utils.llm import generate_response, extract_text
from langchain_core.messages import AIMessage


def _strip_fences(text: str) -> str:
    match = re.search(r"```(?:\w+)?\n(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()


def fix_agent(state):
    print("Running Fix Agent...")

    original_code = state.get("code", "")
    current_code  = state.get("fixed_code") or original_code
    analysis      = state.get("analysis", "")
    messages      = state.get("messages", [])
    language      = state.get("language", "python")

    if not analysis or "no issues found" in analysis.lower():
        print("Fix Agent: nothing to fix.")
        return {
            "fixed_code": current_code,
            "messages":   messages,
            "next_agent": "execution_agent",  
        }

    # each bug is one line starting with [CATEGORY]
    bug_lines = [
        l.strip() for l in analysis.splitlines()
        if l.strip() and l.strip().startswith("[")
    ]
    if not bug_lines:
        bug_lines = [analysis.strip()]

    print(f"Fix Agent: fixing {len(bug_lines)} bugs one by one...")

    for i, bug in enumerate(bug_lines):
        print(f"  Fixing bug {i+1}/{len(bug_lines)}: {bug[:80]}")

        prompt = f"""Fix this one bug in the {language} code.

Bug:
{bug}

Current code:
{current_code}

Rules:
- Fix ONLY this specific bug
- Keep every other line exactly the same
- Do NOT remove any functions or endpoints
- Return the COMPLETE fixed code with no truncation

Fixed code:"""

        try:
            raw   = extract_text(generate_response(prompt))
            fixed = _strip_fences(raw)

            if fixed and len(fixed) > 30 and len(fixed) >= len(current_code) * 0.5:
                current_code = fixed
                print(f"    ✓ Bug {i+1} fixed ({len(current_code)} chars)")
            else:
                print(f"    ✗ Bug {i+1} — unusable output, skipping")
        except Exception as e:
            print(f"    ✗ Bug {i+1} — exception: {e}")

    print(f"Fix Agent done. Final code: {len(current_code)} chars.")

    return {
        "fixed_code": current_code,
        "messages":   messages + [AIMessage(content=current_code)],
        "next_agent": "execution_agent",  
    }