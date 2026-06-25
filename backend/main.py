import os
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

# وارد کردن توابعی که در مراحل قبل ساختیم
from vector_store import extract_and_chunk_pdf, SimpleVectorStore

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vector_store = SimpleVectorStore()

@app.on_event("startup")
async def load_pdf_data():
    pdf_path = "document.pdf"
    if os.path.exists(pdf_path):
        print(f"Loading and indexing {pdf_path}...")
        chunks = extract_and_chunk_pdf(pdf_path)
        vector_store.add_documents(chunks)
    else:
        print(f"Warning: {pdf_path} not found. Please place it in the root directory.")

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    relevant_chunks = vector_store.search(request.message, top_k=3)
    
    context = "\n---\n".join(relevant_chunks)
    
    system_prompt = (
        "You are an intelligent assistant. Use the following pieces of retrieved context to answer the user's question. "
        "If you don't know the answer or if it's not present in the context, just say that you don't know, "
        "do not try to make up an answer. Keep the answer concise and respond in the same language as the context/question (Persian).\n\n"
        f"Context:\n{context}"
    )

    response = client.chat.completions.create(
        model="my-qwen3",
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

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)