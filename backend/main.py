import os

from dotenv import load_dotenv
import google.generativeai as genai

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

genai.configure(api_key=GOOGLE_API_KEY)

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


@app.post("/chat")
async def chat(request: ChatRequest):
    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(
        request.message,
        stream=True
    )

    async def generate():
        for chunk in response:
            if hasattr(chunk, "text") and chunk.text:
                yield chunk.text

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )