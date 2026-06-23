from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class ChatRequest(BaseModel):
    message: str

async def generate_response(msg: str):
    response_text = f"سلام! من پیام شما ('{msg}') را دریافت کردم و این یک پاسخ استریم شده است."
    
    for char in response_text:
        yield char
        await asyncio.sleep(0.03)

@app.post("/chat")
async def chat(request: ChatRequest):
    return StreamingResponse(generate_response(request.message), media_type="text/event-stream")

# uvicorn main:app --reload --port 8000