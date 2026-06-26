from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from config import AI_CLIENT, AI_MODEL_NAME
from schemas import ChatRequest
from security import get_current_user_from_cookie
from vector_store import SimpleVectorStore

router = APIRouter(tags=["Chat"])

def get_vector_store():
    store = SimpleVectorStore()
    return store


@router.post("/chat")
async def chat(
    request: ChatRequest, 
    current_user: str = Depends(get_current_user_from_cookie),
    vector_store: SimpleVectorStore = Depends(get_vector_store)
):
    relevant_chunks = vector_store.search(request.message, top_k=3)
    context = "\n---\n".join(relevant_chunks)
    
    system_prompt = (
        "You are an intelligent assistant. Use the following pieces of retrieved context to answer the user's question. "
        "If you don't know the answer or if it's not present in the context, just say that you don't know, "
        "do not try to make up an answer. Keep the answer concise and respond in the same language as the context/question (Persian).\n\n"
        f"Context:\n{context}"
    )

    response = AI_CLIENT.chat.completions.create(
        model=AI_MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.message}
        ],
        stream=True
    )

    def generate():
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    return StreamingResponse(generate(), media_type="text/event-stream")