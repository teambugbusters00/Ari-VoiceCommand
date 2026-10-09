import os
import json
import time
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import httpx

app = FastAPI(title="Ari VoiceCommand Cloud Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama-3.3-70b-versatile")

SYSTEM_DEFAULT = (
    "You are Ari, an intelligent desktop voice assistant and maid for Windows. "
    "You fluently understand and speak both Hindi and English (and Hinglish). "
    "Keep responses helpful, polite, and concise."
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = None
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1024
    stream: Optional[bool] = False

@app.get("/")
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Ari-VoiceCommand Backend",
        "version": "1.0.0",
        "has_groq_key": bool(GROQ_API_KEY),
        "has_gemini_key": bool(GEMINI_API_KEY),
        "has_openai_key": bool(OPENAI_API_KEY),
    }

@app.get("/v1/models")
def list_models():
    return {
        "object": "list",
        "data": [
            {"id": "llama-3.3-70b-versatile", "object": "model", "owned_by": "groq"},
            {"id": "llama3-70b-8192", "object": "model", "owned_by": "groq"},
            {"id": "gemini-2.5-flash", "object": "model", "owned_by": "google"},
            {"id": "gpt-4o-mini", "object": "model", "owned_by": "openai"},
        ]
    }

@app.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest):
    target_model = req.model or DEFAULT_MODEL
    messages = [m.model_dump() for m in req.messages]

    if not any(m.get("role") == "system" for m in messages):
        messages.insert(0, {"role": "system", "content": SYSTEM_DEFAULT})

    api_key = GROQ_API_KEY or os.getenv("GROQ_API_KEY", "")
    base_url = "https://api.groq.com/openai/v1/chat/completions"

    if not api_key:
        if GEMINI_API_KEY:
            api_key = GEMINI_API_KEY
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
            if "llama" in target_model.lower():
                target_model = "gemini-2.5-flash"
        elif OPENAI_API_KEY:
            api_key = OPENAI_API_KEY
            base_url = "https://api.openai.com/v1/chat/completions"
            if "llama" in target_model.lower():
                target_model = "gpt-4o-mini"
        else:
            return JSONResponse(
                status_code=200,
                content={
                    "id": f"chatcmpl-{int(time.time())}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": target_model,
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "नमस्ते! Ari Voice Assistant Backend is active. Please add GROQ_API_KEY in the Hugging Face Space / Server Settings to enable full AI responses."
                        },
                        "finish_reason": "stop"
                    }]
                }
            )

    payload = {
        "model": target_model,
        "messages": messages,
        "temperature": req.temperature,
        "max_tokens": req.max_tokens,
        "stream": req.stream,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    client = httpx.AsyncClient(timeout=60.0)

    if req.stream:
        async def stream_generator():
            try:
                async with client.stream("POST", base_url, json=payload, headers=headers) as response:
                    async for line in response.aiter_lines():
                        if line:
                            yield f"{line}\n\n"
            finally:
                await client.aclose()
        return StreamingResponse(stream_generator(), media_type="text/event-stream")
    else:
        try:
            resp = await client.post(base_url, json=payload, headers=headers)
            await client.aclose()
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=resp.text)
            return resp.json()
        except Exception as e:
            await client.aclose()
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
