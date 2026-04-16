import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from dotenv import load_dotenv
from typing import Any
import os

load_dotenv()

HF_MODEL_NAME = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
HF_HUB        = os.getenv("HF_HUB", "")
MAX_TOKENS    = 1024

hf_model     = None
hf_tokenizer = None


def load_hf_model():
    global hf_model, hf_tokenizer

    if hf_model is not None:
        return hf_model, hf_tokenizer

    print("Loading Qwen2.5-Coder-1.5B model (ONLY ONCE)...")

    hf_tokenizer = AutoTokenizer.from_pretrained(
        HF_MODEL_NAME,
        token=HF_HUB if HF_HUB else None,
    )

    hf_model = AutoModelForCausalLM.from_pretrained(
        HF_MODEL_NAME,
        token=HF_HUB if HF_HUB else None,
        dtype=torch.float16,        
        device_map="auto",
        low_cpu_mem_usage=True,
    )

    print("Model loaded successfully.")
    return hf_model, hf_tokenizer


def extract_text(response: Any) -> str:
    if response is None:
        return ""
    if isinstance(response, str):
        return response.strip()
    if isinstance(response, dict):
        return str(response.get("content", response)).strip()
    if hasattr(response, "content"):
        return str(response.content).strip()
    return str(response).strip()


def generate_response(prompt: str) -> str:
    model, tokenizer = load_hf_model()

    messages = [
        {
            "role":    "system",
            "content": "You are a senior debugging engineer. Follow instructions exactly."
        },
        {
            "role":    "user",
            "content": prompt
        }
    ]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs    = tokenizer(text, return_tensors="pt").to(model.device)
    input_len = inputs["input_ids"].shape[1]

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_TOKENS,
            do_sample=False,             
            temperature=None,            
            top_p=None,                   
            # top_k removed — causes "not valid" warning with do_sample=False
            pad_token_id=tokenizer.eos_token_id,
            repetition_penalty=1.1,
        )

    new_tokens = outputs[0][input_len:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()