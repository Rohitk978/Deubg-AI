from utils.llm import get_llm
from pydantic import BaseModel
import json

llm = get_llm()



def evaluator_agent(state):
    print("Running Evaluator...")
    score: float
    reasoning: str

    problem = state["messages"][-1].content
    solution = state.get("tool_result","")
    prompt = f"""
You are a senior code reviewer.

Evaluate whether the proposed debugging solution correctly fixes the problem.

Problem:
{problem}

Proposed Solution:
{solution}

Return JSON:

{{
"score": number between 0 and 1,
"reason": "short evaluation"
}}
"""
    response = llm.invoke(prompt)
    try:
        parsed = json.loads(response.content)
        result = evaluator_agent(**parsed)
        score = result.score
        
    except Exception:
            score = 0.3
    return {
            "evaluation_score":score,
            "next_agent":"supervisor"
        }
    