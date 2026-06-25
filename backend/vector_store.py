import numpy as np
import faiss
from openai import OpenAI

ollama_client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

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