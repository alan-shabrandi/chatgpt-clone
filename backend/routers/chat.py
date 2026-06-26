import os
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from openai import OpenAI

from config import OLLAMA_URL
from schemas import ChatRequest
from security import get_current_user_from_cookie
from vector_store import SimpleVectorStore

router = APIRouter(tags=["Chat"])
vector_store = SimpleVectorStore()

# ۱. بررسی وجود کلید ابری OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if OPENROUTER_API_KEY:
    # اتصال به کلاینت ابری ابری و رایگان
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY
    )
    # مدل پیشنهادی با کیفیت و پرسرعت Qwen 2.5 نسخه‌ی 72 میلیارد پارامتری
    AI_MODEL_NAME = "qwen/qwen-2.5-72b-instruct"
else:
    # بازگشت به تنظیمات Ollama لوکال در صورت عدم وجود کلید ابری
    client = OpenAI(base_url=OLLAMA_URL, api_key="ollama")
    AI_MODEL_NAME = "my-qwen3"


@router.post("/chat")
async def chat(request: ChatRequest, current_user: str = Depends(get_current_user_from_cookie)):
    relevant_chunks = vector_store.search(request.message, top_k=3)
    context = "\n---\n".join(relevant_chunks)
    
    system_prompt = (
        "You are an intelligent assistant. Use the following pieces of retrieved context to answer the user's question. "
        "If you don't know the answer or if it's not present in the context, just say that you don't know, "
        "do not try to make up an answer. Keep the answer concise and respond in the same language as the context/question (Persian).\n\n"
        f"Context:\n{context}"
    )

    # ۲. استفاده از متغیر داینامیک AI_MODEL_NAME برای مدل
    response = client.chat.completions.create(
        model=AI_MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.message}
        ],
        stream=True
    )

    def generate():
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    return StreamingResponse(generate(), media_type="text/event-stream")