import numpy as np
import faiss
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI

ollama_client = OpenAI(
    base_url="http://localhost:11434/v1",
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
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []

    def get_embedding(self, text: str) -> list:
        response = ollama_client.embeddings.create(
            model="nomic-embed-text",
            input=text
        )
        return response.data[0].embedding

    def add_documents(self, chunks: list):
        if not chunks:
            return
            
        embeddings = []
        for chunk in chunks:
            emb = self.get_embedding(chunk)
            embeddings.append(emb)
            self.documents.append(chunk)
            
        np_embeddings = np.array(embeddings).astype('float32')
        self.index.add(np_embeddings)
        print(f"Successfully indexed {len(chunks)} chunks.")

    def search(self, query: str, top_k: int = 3):
        query_emb = np.array([self.get_embedding(query)]).astype('float32')
        distances, indices = self.index.search(query_emb, top_k)
        
        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.documents):
                results.append(self.documents[idx])
        return results