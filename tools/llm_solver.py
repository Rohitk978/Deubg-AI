from utils.llm import generate_response
from config import LLM_PROVIDER
from utils.language_detector import detect_language

# llm = get_llm(LLM_PROVIDER)

def llm_solve(problem,analysis):
    """ LLM_based debugging instead of execution."""
    language = detect_language(problem)


    prompt = f"""
You are a senior software engineer.

Code:
{problem}

Language : {language}

Analysis:
{analysis}

Fix the code and explain.

Return STRICT format:

### Error Explanation
### Root Cause
### Fixed Code
### Improvements
### Complexity
"""
    
    response = generate_response(prompt)
    return response.content