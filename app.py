import os
from flask import Flask, jsonify, request, render_template
from langchain_core.messages import HumanMessage, AIMessage
from graph.builder import build_graph
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
conversation = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/debug", methods=["POST"])
def debug():
    data       = request.json
    user_input = data.get("input", "")
    mode       = data.get("mode", "both")

    if not user_input:
        return jsonify({"solution": "No input provided.", "analysis": "", "tool_used": mode})

    conversation.append(HumanMessage(content=user_input))

    selected_tool = "llm_solver"
    if mode == "web":
        selected_tool = "web_search"
    elif mode == "both":
        selected_tool = "both"

    state = {
        "messages": conversation,
        "code": user_input,
        "iteration":0,
        "selected_tool":selected_tool,
        "fix_attempts":0,
        "max_fix_attempts":3,
    }

    graph  = build_graph(state)
    result = graph.invoke(state)

    final_answer = (
        result.get("output")
        or result.get("final_answer")
        or result.get("analysis")
        or "Pipeline completed but produced no output."
    )

    conversation.append(AIMessage(content=final_answer))

    return jsonify({
        "solution":final_answer,
        "analysis":result.get("analysis", ""),
        "tool_used":result.get("selected_tool", mode),
    })


if __name__ == "__main__":
    # Set DEBUG=true in .env for development, leave unset in production
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode, use_reloader=False)
