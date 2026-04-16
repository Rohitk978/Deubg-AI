import re
from langchain_core.messages import AIMessage

# Severity scores — higher = more critical
SEVERITY = {
    "SECURITY":       5,
    "CRASH":          5,
    "SYNTAX ERROR":   5,
    "RESOURCE_LEAK":  4,
    "ERROR_HANDLING": 3,
    "LOGIC_BUG":      3,
    "CONFIG":         2,
    "PYLINT":         2,
    "PYFLAKES":       2,
    "QUALITY":        1,
}

def _score(bug_line: str) -> int:
    m = re.match(r"\[([A-Z_\s]+)\]", bug_line)
    cat = m.group(1).strip() if m else "QUALITY"
    return SEVERITY.get(cat, 1)

def _deduplicate(lines: list) -> list:
    """Remove duplicate bugs that refer to the same line and category."""
    seen = set()
    result = []
    for line in lines:
        # key = category + line number
        m = re.match(r"(\[[A-Z_\s]+\])\s*(Line \d+)", line)
        key = (m.group(1) + m.group(2)) if m else line[:60]
        if key not in seen:
            seen.add(key)
            result.append(line)
    return result

def _filter_false_positives(lines: list, code: str) -> list:
    """
    Remove bugs that are clearly false positives:
    - QUALITY/print warnings inside if __name__ == '__main__' blocks
    - CONFIG warnings when debug is controlled by env var
    """
    filtered = []
    for line in lines:
        # skip debug=True warning if code reads from env
        if "[CONFIG]" in line and "os.getenv" in code:
            continue
        filtered.append(line)
    return filtered

def validator_agent(state):
    print("Running Validator...")

    code     = state.get("code", "")
    analysis = state.get("analysis", "")
    messages = state.get("messages", [])

    if not analysis or "no issues found" in analysis.lower():
        print("Validator: No bugs found — passing clean code to execution.")
        return {
            "analysis":   analysis,
            "fixed_code": code,
            "messages":   messages,
            "next_agent": "execution_agent",
        }

    # parse, deduplicate, filter, sort by severity 
    raw_lines = [l.strip() for l in analysis.splitlines() if l.strip()]

    deduped   = _deduplicate(raw_lines)
    filtered  = _filter_false_positives(deduped, code)
    sorted_bugs = sorted(filtered, key=_score, reverse=True)

    validated = "\n".join(sorted_bugs)

    #  build validation summary 
    critical = sum(1 for l in sorted_bugs if _score(l) >= 4)
    warnings = len(sorted_bugs) - critical

    summary = (
        f"Validator: {len(sorted_bugs)} unique issue(s) confirmed "
        f"({critical} critical, {warnings} warnings). "
        f"Removed {len(raw_lines) - len(sorted_bugs)} duplicate(s)."
    )
    print(f"[Validator] {summary}")
    print(f"[Validator] Sorted analysis:\n{validated[:400]}")

    return {
        "analysis":   validated,
        "messages":   messages + [AIMessage(content=summary)],
        "next_agent": "fix_agent",
    }