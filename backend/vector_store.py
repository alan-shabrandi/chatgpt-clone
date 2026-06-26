import psycopg2
from psycopg2.extras import execute_values
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import DATABASE_URL, AI_CLIENT, EMBEDDING_MODEL, DEFAULT_DIMENSION


def extract_and_chunk_pdf(file_path: str, chunk_size: int = 600, chunk_overlap: int = 100) -> list[str]:
    reader = PdfReader(file_path)
    full_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    return text_splitter.split_text(full_text)


class SimpleVectorStore:
    def __init__(self, dimension: int = DEFAULT_DIMENSION):
        self.dimension = dimension

    def _get_connection(self):
        return psycopg2.connect(DATABASE_URL)

    def init_db(self):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
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
            conn.commit()

    def get_embedding(self, text: str) -> list[float]:
        response = AI_CLIENT.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding

    def add_documents(self, chunks: list[str]):
        if not chunks:
            return
            
        with self._get_connection() as conn:
            data_to_insert = []
            for chunk in chunks:
                try:
                    emb = self.get_embedding(chunk)
                    data_to_insert.append((chunk, emb))
                except Exception as e:
                    print(f"Error generating embedding for chunk: {e}")
                    continue
            
            if data_to_insert:
                with conn.cursor() as cur:
                    execute_values(
                        cur,
                        "INSERT INTO documents (content, embedding) VALUES %s",
                        data_to_insert
                    )
                conn.commit()
                print(f"Successfully indexed {len(data_to_insert)} chunks.")

    def search(self, query: str, top_k: int = 3) -> list[str]:
        query_emb = self.get_embedding(query)
        
        with self._get_connection() as conn:
            with conn.cursor() as cur:
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