import os
import psycopg2
from psycopg2.extras import execute_values
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI

# خواندن متغیرهای محیطی از داکر
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://myuser:mypassword@localhost:5432/mydb")

ollama_client = OpenAI(
    base_url=OLLAMA_URL,
    api_key="ollama",
)

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
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        # اتصال به دیتابیس PostgreSQL
        self.conn = psycopg2.connect(DATABASE_URL)
        self.create_table()

    def create_table(self):
        with self.conn.cursor() as cur:
            # فعال‌سازی افزونه pgvector در دیتابیس
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            # ساخت جدول ذخیره‌سازی متن و وکتور (اگر از قبل نباشد)
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    content TEXT,
                    embedding vector({self.dimension})
                );
            """)
            self.conn.commit()

    def get_embedding(self, text: str) -> list:
        response = ollama_client.embeddings.create(
            model="nomic-embed-text",
            input=text
        )
        return response.data[0].embedding

    def add_documents(self, chunks: list):
        if not chunks:
            return
            
        # بررسی برای جلوگیری از ذخیره تکراری (در صورت تمایل می‌توانید این شرط را بردارید)
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM documents;")
            if cur.fetchone()[0] > 0:
                print("Database already indexed. Skipping...")
                return

        data_to_insert = []
        for chunk in chunks:
            emb = self.get_embedding(chunk)
            data_to_insert.append((chunk, emb))
            
        # درج دسته‌جمعی و سریع داده‌ها در دیتابیس
        with self.conn.cursor() as cur:
            execute_values(
                cur,
                "INSERT INTO documents (content, embedding) VALUES %s",
                data_to_insert
            )
            self.conn.commit()
        print(f"Successfully indexed {len(chunks)} chunks into PostgreSQL.")

    def search(self, query: str, top_k: int = 3):
        query_emb = self.get_embedding(query)
        
        with self.conn.cursor() as cur:
            # استفاده از عملگر <=> برای محاسبه فاصله کسینوسی (Cosine Distance) در pgvector
            cur.execute(
                """
                SELECT content FROM documents 
                ORDER BY embedding <=> %s::vector 
                LIMIT %s;
                """,
                (query_emb, top_k)
            )
            rows = cur.fetchall()
            
        # استخراج متن‌ها از خروجی دیتابیس
        return [row[0] for row in rows]