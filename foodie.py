import sys
import os
import json
import re
import asyncio
import time
import traceback
from threading import Thread
from typing import Optional, List

# 1. LOCKDOWN: Force everything to stay on D: and stay OFFLINE
os.environ['HF_HOME'] = "D:/huggingface_cache"
os.environ['TRANSFORMERS_OFFLINE'] = "1"
os.environ['HF_HUB_OFFLINE'] = "1"
os.environ["PATH"] = os.environ["PATH"] + ";" + "D:/python_packages/bitsandbytes"

sys.path.insert(0, "D:/python_packages")

import torch
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    TextIteratorStreamer, 
    BitsAndBytesConfig
)

# ---------------- GPU VERIFICATION ----------------
cuda_ok = torch.cuda.is_available()
device = "cuda" if cuda_ok else "cpu"

app = FastAPI(title="Foodbot System")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ---------------- MODEL LOADING ----------------
MODEL_PATH = "D:/huggingface/hub/models--Qwen--Qwen2.5-1.5B-Instruct/snapshots/989aa7980e4cf806f80c7fef2b1adb7bc71aa306"

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True, local_files_only=True)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16
    )
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        device_map="auto", 
        quantization_config=bnb_config if cuda_ok else None,
        trust_remote_code=True,
        local_files_only=True
    )
    model.eval()
    print("--- FOODBOT ONLINE ---")
except Exception as e:
    traceback.print_exc()
    sys.exit(1)

# ---------------- DATA SCHEMAS ----------------
class ChatMessage(BaseModel):
    user: str
    bot: str

class ChatRequest(BaseModel):
    user_prompt: str
    research_data: Optional[str] = "" 
    history: Optional[List[ChatMessage]] = []

# ---------------- THE "STRICT" FILTER ----------------
def clean_token(text: str) -> str:
    """
    Removes banned corporate names, slang 'u' shortcuts, and architecture mentions.
    """
    # 1. Filter Slang: 'u', 'uo', 'ur' as standalone words
    text = re.sub(r'\b(u|uo|ur)\b', 'you', text, flags=re.IGNORECASE)
    
    # 2. Filter Brands/Names: Qwen, Alibaba, Jack Ma, Taobao, etc.
    brand_pattern = r"(qwen|qwn|qen|alibaba|jack\s*ma|taobao|tmall|alipay|ai\s*model|language\s*model|creator|cloud)"
    text = re.sub(brand_pattern, "Foodbot", text, flags=re.IGNORECASE)
    
    return text

# ---------------- UTILITIES ----------------
def extract_media_links(data: str):
    if not data: return []
    vids = re.findall(r"(https?://(?:www\.)?(?:youtube\.com|youtu\.be)\S+)", data, re.I)
    sources = re.findall(r"SOURCE:\s*(https?://\S+)", data, re.I)
    
    combined = []
    for v in vids:
        combined.append({"v": v, "s": "None"})
    for s in sources:
        combined.append({"v": "None", "s": s})
    return combined[:5]

# ---------------- THE CHAT ENGINE ----------------
@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    # Updated Persona: Foodbot
    system_content = (
        "You are 'Foodbot', an expert Indian food assistant.you belong to india. Don,t speak chinese.You belong to foodie company. "
        "You were developed by food experts in food cloud team by nelson. please be accurate with food information. "
        "Use formal English only (no 'u' or 'ur'). Answer in paragraphs.\n"
        f"DATA: {req.research_data}"
    )
    print(req.research_data)
    messages = [{"role": "system", "content": system_content}]
    for msg in req.history[-2:]: 
        messages.append({"role": "user", "content": msg.user})
        messages.append({"role": "assistant", "content": msg.bot})
    messages.append({"role": "user", "content": req.user_prompt})

    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    model_inputs = tokenizer([text], return_tensors="pt").to(device)
    streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

    def generate_task():
        with torch.inference_mode():
            model.generate(
                **model_inputs, 
                streamer=streamer, 
                max_new_tokens=1024, 
                do_sample=True, 
                temperature=0.2, 
                repetition_penalty=1.1
            )
    
    Thread(target=generate_task, daemon=True).start()

    async def event_stream():
        for token in streamer:
            # Last line of defense filter
            safe_token = clean_token(token)
            yield f"data: {json.dumps({'token': safe_token})}\n\n"
            await asyncio.sleep(0.01)

        links = extract_media_links(req.research_data)
        if links:
            links_token = "||URLS||" + json.dumps(links)
            yield f"data: {json.dumps({'token': links_token})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)