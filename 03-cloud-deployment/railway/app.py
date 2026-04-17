"""
Agent Railway-ready.
Railway inject PORT env var tự động — agent phải dùng os.getenv("PORT").
"""
import os
import time
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from utils.mock_llm import ask as mock_ask

# Cấu hình OpenAI (Nếu có)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AGENT_API_KEY = os.getenv("AGENT_API_KEY")

if OPENAI_API_KEY:
    import openai
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
else:
    client = None

app = FastAPI(title="Agent on Railway", version="1.0.0")
START_TIME = time.time()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "AI Agent running on Railway!",
        "docs": "/docs",
        "health": "/health",
    }

@app.post("/ask")
async def ask_agent(request: Request):
    # 1. Kiểm tra API Key (Security)
    if AGENT_API_KEY:
        auth_header = request.headers.get("X-API-Key")
        if auth_header != AGENT_API_KEY:
            raise HTTPException(401, "Unauthorized: Invalid API Key")

    body = await request.json()
    question = body.get("question", "")
    if not question:
        raise HTTPException(422, "question required")

    # 2. Logic chọn LLM: Thật vs Mock
    if client:
        try:
            response = client.chat.completions.create(
                model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
                messages=[{"role": "user", "content": question}],
                max_tokens=200
            )
            answer = response.choices[0].message.content
        except Exception as e:
            answer = f"Error calling OpenAI: {str(e)}"
    else:
        answer = mock_ask(question)

    return {
        "question": question,
        "answer": answer,
        "platform": "Railway",
        "llm_type": "OpenAI" if client else "Mock"
    }


@app.get("/health")
def health():
    """
    Railway sẽ check endpoint này định kỳ.
    Trả về 200 = healthy. Non-200 = Railway restart container.
    """
    return {
        "status": "ok",
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "platform": "Railway",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    # ✅ Railway inject PORT — PHẢI đọc từ env
    port = int(os.getenv("PORT", 8000))
    print(f"Starting on port {port} (from PORT env var)")
    uvicorn.run(app, host="0.0.0.0", port=port)
