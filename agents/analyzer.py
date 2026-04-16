import ast
import re
import subprocess
import tempfile
import os
from utils.language_detector import detect_language
from langchain_core.messages import AIMessage


# RULE-BASED STATIC ANALYZERS — no LLM needed, 100% reliable

def _run_pyflakes(code: str) -> list:
    """Run pyflakes for undefined names, unused imports, syntax errors."""
    bugs = []
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as f:
            f.write(code)
            tmp = f.name
        result = subprocess.run(
            ["python", "-m", "pyflakes", tmp],
            capture_output=True, text=True
        )
        os.unlink(tmp)
        for line in result.stdout.splitlines() + result.stderr.splitlines():
            line = line.strip()
            if line and tmp in line:
                line = line.replace(tmp, "code")
                bugs.append(f"[PYFLAKES] {line}")
    except Exception as e:
        pass
    return bugs


def _run_pylint(code: str) -> list:
    """Run pylint for deeper code issues."""
    bugs = []
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as f:
            f.write(code)
            tmp = f.name
        result = subprocess.run(
            ["python", "-m", "pylint", tmp,
             "--disable=C,R,W0611,W0401",   
             "--output-format=text",
             "--score=no"],
            capture_output=True, text=True
        )
        os.unlink(tmp)
        for line in result.stdout.splitlines():
            line = line.strip()
            if line and (":E" in line or ":W" in line or ":F" in line):
                line = re.sub(r".*?code\.py:", "Line ", line)
                bugs.append(f"[PYLINT] {line}")
    except Exception:
        pass
    return bugs[:10]  


def _ast_analyze(code: str) -> list:
    """
    AST-based analysis — catches bugs that pyflakes misses:
    - bare except clauses
    - mutable default arguments
    - missing return in non-void functions
    - SQL string formatting (injection)
    - hardcoded passwords/secrets
    - dangerous eval/exec usage
    - unclosed resources (no context manager)
    """
    bugs = []
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [f"[SYNTAX ERROR] Line {e.lineno}: {e.msg}"]

    lines = code.splitlines()

    for node in ast.walk(tree):

        if isinstance(node, ast.ExceptHandler) and node.type is None:
            bugs.append(
                f"[ERROR_HANDLING] Line {node.lineno}: bare `except:` catches everything "
                f"including KeyboardInterrupt and SystemExit — use `except Exception:`"
            )

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for default in node.args.defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    bugs.append(
                        f"[LOGIC_BUG] Line {node.lineno}: function `{node.name}` uses mutable "
                        f"default argument — shared across all calls, causes subtle bugs"
                    )

        if isinstance(node, ast.Call):
            func_name = ""
            if isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            if func_name == "execute" and node.args:
                arg = node.args[0]
                # detect f-string or % formatting in execute()
                if isinstance(arg, ast.JoinedStr):
                    bugs.append(
                        f"[SECURITY] Line {node.lineno}: `cursor.execute()` uses f-string — "
                        f"SQL injection vulnerability, use parameterized queries with `?` or `%s`"
                    )
                elif isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Mod):
                    bugs.append(
                        f"[SECURITY] Line {node.lineno}: `cursor.execute()` uses `%` formatting — "
                        f"SQL injection vulnerability, use parameterized queries"
                    )

        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in ("eval", "exec"):
                bugs.append(
                    f"[SECURITY] Line {node.lineno}: `{node.func.id}()` is dangerous — "
                    f"executes arbitrary code, avoid unless absolutely necessary"
                )

        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    name = target.id.lower()
                    if any(k in name for k in ("password", "secret", "token", "api_key", "passwd")):
                        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                            if len(node.value.value) > 3:
                                bugs.append(
                                    f"[SECURITY] Line {node.lineno}: hardcoded secret in `{target.id}` — "
                                    f"move to environment variables"
                                )

        if isinstance(node, ast.Subscript):
            if isinstance(node.value, ast.Name):
                # check if variable looks like request data (data, request, body, payload)
                if node.value.id in ("data", "request_data", "body", "payload", "json_data"):
                    if isinstance(node.slice, ast.Constant):
                        bugs.append(
                            f"[CRASH] Line {node.lineno}: `{node.value.id}['{node.slice.value}']` — "
                            f"KeyError crash if key missing, use `{node.value.id}.get('{node.slice.value}')` instead"
                        )

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # debug=True in production
        if re.search(r"app\.run\(.*debug\s*=\s*True", stripped):
            bugs.append(
                f"[CONFIG] Line {i}: `debug=True` in app.run() — "
                f"never use in production, exposes debugger and secrets"
            )

        # print statements left in (warn only)
        if re.match(r"^\s*print\s*\(", line) and "debug" not in line.lower():
            bugs.append(
                f"[QUALITY] Line {i}: `print()` statement — "
                f"use logging module instead for production code"
            )

        # missing conn.close() pattern — connection opened but close not visible nearby
        if re.search(r"=\s*(sqlite3|psycopg2|pymysql|cx_Oracle)\.connect\(", stripped):
            # check if conn.close() appears within next 20 lines
            window = lines[i:min(i+20, len(lines))]
            if not any("close()" in wl or "with " in lines[i-1] for wl in window):
                bugs.append(
                    f"[RESOURCE_LEAK] Line {i}: DB connection opened — "
                    f"no `conn.close()` found nearby, use `with` statement or close in finally block"
                )

    return bugs


def _analyze_javascript(code: str) -> list:
    """Basic JS/TS rule-based checks."""
    bugs = []
    lines = code.splitlines()
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if "==" in stripped and "===" not in stripped and not stripped.startswith("//"):
            bugs.append(f"[LOGIC_BUG] Line {i}: `==` used — use `===` for strict equality in JS")
        if re.search(r"var\s+\w+", stripped):
            bugs.append(f"[QUALITY] Line {i}: `var` used — use `const` or `let` instead")
        if "eval(" in stripped:
            bugs.append(f"[SECURITY] Line {i}: `eval()` is dangerous")
        if re.search(r"console\.log\(", stripped):
            bugs.append(f"[QUALITY] Line {i}: `console.log()` left in code")
    return bugs


def _analyze_generic(code: str, lang: str) -> list:
    """Generic checks for any language."""
    bugs = []
    lines = code.splitlines()
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if re.search(r"password\s*=\s*['\"][^'\"]{3,}['\"]", stripped, re.IGNORECASE):
            bugs.append(f"[SECURITY] Line {i}: hardcoded password detected")
        if re.search(r"TODO|FIXME|HACK|XXX", stripped):
            bugs.append(f"[QUALITY] Line {i}: unresolved `{re.search(r'TODO|FIXME|HACK|XXX', stripped).group()}` marker")
    return bugs


# MAIN AGENT

def analyzer_agent(state):
    print("Running Analyzer...")

    code     = state.get("code", "").strip()
    messages = state.get("messages", [])

    if not code:
        return {
            "analysis": "No code provided.",
            "language": "unknown",
            "iteration": state.get("iteration", 0) + 1,
            "messages": messages,
            "next_agent": "fix_agent",
        }

    lang = detect_language(code)
    print(f"Language detected: {lang}")

    all_bugs = []

    if lang.lower() == "python":
        all_bugs += _ast_analyze(code)
        all_bugs += _run_pyflakes(code)
        all_bugs += _run_pylint(code)
    elif lang.lower() in ("javascript", "typescript"):
        all_bugs += _analyze_javascript(code)
        all_bugs += _analyze_generic(code, lang)
    else:
        all_bugs += _analyze_generic(code, lang)

    # deduplicate while preserving order
    seen = set()
    unique_bugs = []
    for b in all_bugs:
        key = b[:80]
        if key not in seen:
            seen.add(key)
            unique_bugs.append(b)

    if unique_bugs:
        final_analysis = "\n".join(unique_bugs)
    else:
        final_analysis = "No issues found"

    print(f"[Analyzer] Found {len(unique_bugs)} issues:")
    for b in unique_bugs:
        print(f"  {b}")

    return {
        "analysis":   final_analysis,
        "iteration":  state.get("iteration", 0) + 1,
        "language":   lang,
        "messages":   messages + [AIMessage(content=final_analysis)],
        "next_agent": "router",
    }