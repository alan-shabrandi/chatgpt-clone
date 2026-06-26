This file is a merged representation of a subset of the codebase, containing specifically included files, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: routers/chat.py, ./vector_store.py
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
./vector_store.py
routers/chat.py
```

# Files

## File: ./vector_store.py
```python
import os
import psycopg2
from psycopg2.extras import execute_values
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://myuser:mypassword@localhost:5432/mydb")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if OPENROUTER_API_KEY:
    embedding_client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY
    )
    EMBEDDING_MODEL = "openai/text-embedding-3-small"
    DEFAULT_DIMENSION = 1536
else:
    embedding_client = OpenAI(
        base_url=OLLAMA_URL,
        api_key="ollama",
    )
    EMBEDDING_MODEL = "nomic-embed-text"
    DEFAULT_DIMENSION = 768

def extract_and_chunk_pdf(file_path: str, chunk_size: int = 600, chunk_overlap: int = 100):
    reader = PdfReader(file_path)
    full_text = ""
    
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
            
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_text(full_text)
    return chunks


class SimpleVectorStore:
    def __init__(self, dimension: int = None):
        self.dimension = dimension if dimension is not None else DEFAULT_DIMENSION
        self.conn = psycopg2.connect(DATABASE_URL)
        self.create_table()

    def create_table(self):
        with self.conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    content TEXT,
                    embedding vector({self.dimension})
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL
                );
            """)
            self.conn.commit()

    def get_embedding(self, text: str) -> list:
        response = embedding_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding

    def add_documents(self, chunks: list):
        if not chunks:
            return
            
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM documents;")
            if cur.fetchone()[0] > 0:
                print("Database already indexed. Skipping...")
                return

        data_to_insert = []
        for chunk in chunks:
            try:
                emb = self.get_embedding(chunk)
                data_to_insert.append((chunk, emb))
            except Exception as e:
                print(f"Error generating embedding for chunk: {e}")
                continue
            
        if data_to_insert:
            with self.conn.cursor() as cur:
                execute_values(
                    cur,
                    "INSERT INTO documents (content, embedding) VALUES %s",
                    data_to_insert
                )
                self.conn.commit()
            print(f"Successfully indexed {len(data_to_insert)} chunks into PostgreSQL.")

    def search(self, query: str, top_k: int = 3):
        query_emb = self.get_embedding(query)
        
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT content FROM documents 
                ORDER BY embedding <=> %s::vector 
                LIMIT %s;
                """,
                (query_emb, top_k)
            )
            rows = cur.fetchall()
            
        return [row[0] for row in rows]
```

## File: routers/chat.py
```python
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

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if OPENROUTER_API_KEY:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY
    )
    AI_MODEL_NAME = "qwen/qwen-2.5-72b-instruct"
else:
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
```
