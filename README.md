# Code Debug AI

A multi-agent AI system that detects, explains, and fixes bugs in source code across 18 programming languages.

---

## Architecture

```
User Code Input
      │
      ▼
┌─────────────┐
│   Analyzer  │  AST + pyflakes + pylint (rule-based, no LLM)
└──────┬──────┘
       │ bug list
       ▼
┌─────────────┐
│    Router   │  picks tool based on bug type
└──────┬──────┘
       │
       ▼
┌──────────────┐
│ Tool Executor│  routes to llm_solver or web_search
└──────┬───────┘
       │
       ▼
┌─────────────┐
│  Validator  │  deduplicates bugs, scores severity, filters false positives
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Fix Agent  │  applies fixes one bug at a time (LLM)
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ Execution Agent  │  syntax check / run (language-aware)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Explainer Agent  │  detailed per-bug explanation + step-by-step solution
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│Reflection Agent  │  passes final report through
└──────────────────┘
       │
       ▼
   Final Output
(bugs + solutions + fixed code)
```

---

## Features

- **Static analysis** using Python AST, pyflakes, and pylint — deterministic, no hallucination
- **18 languages supported** — Python, JavaScript, TypeScript, Java, C, C++, Go, Rust, PHP, Ruby, Kotlin, Swift, Bash, R, Scala, Perl, Lua, Dart, Haskell
- **Bug categories detected** — SQL injection, KeyError crashes, resource leaks, bare except, mutable defaults, hardcoded secrets, eval/exec, debug=True in production, JS loose equality, var usage
- **Severity scoring** — critical bugs (SECURITY, CRASH) fixed before warnings
- **Multi-language execution** — compiles/runs code to verify fixes work
- **Detailed explanations** — every bug explained with root cause and step-by-step fix

---

## Example — Flask API with multiple bugs

**Input (buggy code):**
```python
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
password = "admin1234"

@app.route("/orders", methods=["POST"])
def create_order():
    data = request.json
    item     = data["item"]
    price    = data["price"]
    quantity = data["quantity"]

    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO orders VALUES ('{item}', {price}, {quantity})")
    conn.commit()

    return jsonify({"message": "Order created"}), 201

if __name__ == "__main__":
    app.run(debug=True)
```

**Output from the AI:**
```
## Code Analysis Report — Python
Found 5 issue(s)

---

### Bug 1 — Security (Line 15)
Detected: [SECURITY] Line 15: cursor.execute() uses f-string — SQL injection vulnerability

What is wrong:
The cursor.execute() call uses an f-string which directly embeds user-supplied
values (item, price, quantity) into the SQL query. This means an attacker can
send crafted input to manipulate or destroy your database.

Why it breaks:
If a user sends item = "'; DROP TABLE orders; --", the resulting query becomes
INSERT INTO orders VALUES (''; DROP TABLE orders; --', ...) which executes two
statements — the second deletes your entire orders table.

Step-by-step solution:
1. Remove the f-string from cursor.execute() entirely
2. Replace embedded variables with ? placeholders
3. Pass actual values as a tuple: cursor.execute("INSERT INTO orders VALUES (?,?,?)", (item, price, quantity))

---

### Bug 2 — Crash Risk (Line 10)
data["item"] — KeyError crash if key missing, use data.get("item") instead

### Bug 3 — Security (Line 5)
Hardcoded secret in `password` — move to environment variables

### Bug 4 — Resource Leak (Line 14)
DB connection opened — no conn.close() found, use `with` statement

### Bug 5 — Configuration (Line 21)
debug=True in app.run() — never use in production

---

### Corrected Code
from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
password = os.getenv("ADMIN_PASSWORD")

@app.route("/orders", methods=["POST"])
def create_order():
    data = request.json
    item     = data.get("item")
    price    = data.get("price")
    quantity = data.get("quantity")

    if not all([item, price, quantity]):
        return jsonify({"error": "Missing required fields"}), 400

    with sqlite3.connect("orders.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO orders VALUES (?, ?, ?)",
            (item, price, quantity)
        )
        conn.commit()

    return jsonify({"message": "Order created"}), 201

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false") == "true")
```

---

## Stack

| Component            | Technology                        |
|----------------------|-----------------------------------|
| Agent orchestration  | LangGraph                         |
| Static analysis      | Python AST, pyflakes, pylint      |
| LLM (fix generation) | Qwen 2.5 Coder 1.5B (local)      |
| Web search           | Tavily API                        |
| Backend              | Flask                             |
| Frontend             | Vanilla JS + Marked.js + Prism.js |

---

## Setup

```bash
git clone https://github.com/yourusername/code-debug-ai
cd code-debug-ai
pip install -r requirements.txt

# add to .env
TAVILY_API_KEY=your_key_here
FLASK_DEBUG=false

python app.py
```

Open `http://localhost:5000`, paste your code, click Send.

---

## What I Learned

- Multi-agent systems need careful state management — bugs in routing caused silent failures that were hard to trace
- Static analysis (deterministic) outperforms LLM-based analysis for bug detection on small models
- A 1.5B model cannot reliably find bugs from scratch but can apply targeted fixes when given precise bug descriptions
- Separating concerns — analyzer finds bugs, LLM only fixes them — gave better results than asking one model to do everything

---

## What I Would Do Differently

- Use Claude or GPT-4o via API for the fix agent instead of a 1.5B local model for higher fix quality
- Add unit tests for each agent to catch routing regressions early
- Add file upload support so users can submit `.py`, `.js`, `.cpp` files directly
- Fine-tune a small model specifically on bug-fix pairs to improve fix accuracy # Debug-AI
