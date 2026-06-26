import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth, chat
from vector_store import extract_and_chunk_pdf

@asynccontextmanager
async def lifespan(app: FastAPI):
    pdf_path = "document.pdf"
    if os.path.exists(pdf_path):
        print(f"Loading and indexing {pdf_path}...")
        chunks = extract_and_chunk_pdf(pdf_path)
        chat.vector_store.add_documents(chunks)
    else:
        print(f"Warning: {pdf_path} not found. Please place it in the root directory.")
    yield

app = FastAPI(lifespan=lifespan)

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://chatgpt-clone-hazel-nine.vercel.app"
]

FRONTEND_URL = os.getenv("FRONTEND_URL")
if FRONTEND_URL:
    ALLOWED_ORIGINS.append(FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)