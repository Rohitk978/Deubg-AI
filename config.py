import os
from dotenv import load_dotenv

load_dotenv()

# FORCE HUGGINGFACE ONLY
LLM_PROVIDER = "hf"

# HUGGINGFACE MODEL
HF_MODEL_NAME = "Qwen2.5-Coder-1.5B-Instruct"
HF_HUB = os.getenv("HF_HUB")

# GENERATION SETTINGS
TEMPERATURE = 0.2

# AGENT SETTINGS
MAX_ITERATIONS = 3
