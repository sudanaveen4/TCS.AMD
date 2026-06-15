import os
import numpy as np
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

class RAGStore:
    def __init__(self, docs_dir):
        self.docs_dir = docs_dir
        self.chunks = []
        self.chunk_sources = []
        
        # We use a small, fast sentence-transformer model suitable for local PC
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print("Failed to load SentenceTransformer:", e)
            self.model = None
            
        self.embeddings = None
        self._build_index()
        
    def _extract_text_from_pdf(self, file_path):
        pass # Replaced by direct text reading

    def _build_index(self):
        if not self.model:
            return
            
        print("Building Vector Store from plant_data...")
        raw_texts = []
        for root, dirs, files in os.walk(self.docs_dir):
            for file in files:
                if file.lower().endswith(('.md', '.txt', '.json')):
                    path = os.path.join(root, file)
                    text = ""
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            text = f.read()
                    except Exception as e:
                        print(f"Failed to read {path}: {e}")
                        continue
                    
                    # Very simple chunking: split by paragraphs
                    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 50]
                    for p in paragraphs:
                        self.chunks.append(p)
                        self.chunk_sources.append(file)
                        
        if not self.chunks:
            print("Warning: No text chunks found for Vector Store.")
            return
            
        print(f"Extracted {len(self.chunks)} chunks. Generating embeddings...")
        embeddings = self.model.encode(self.chunks, show_progress_bar=False)
        embeddings = np.array(embeddings).astype('float32')
        
        # Normalize embeddings for cosine similarity
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        self.embeddings = embeddings / np.where(norms == 0, 1e-10, norms)
        print("Vector Store Ready!")

    def retrieve_context(self, query, k=3):
        if self.embeddings is None or not self.model:
            return "Knowledge base not available."
            
        q_emb = self.model.encode([query]).astype('float32')
        q_norm = np.linalg.norm(q_emb, axis=1, keepdims=True)
        q_emb = q_emb / np.where(q_norm == 0, 1e-10, q_norm)
        
        # Cosine similarity using dot product
        similarities = np.dot(self.embeddings, q_emb.T).flatten()
        
        # Get top k indices
        top_indices = np.argsort(similarities)[::-1][:k]
        
        context = ""
        for idx in top_indices:
            if idx < len(self.chunks):
                context += f"[Source: {self.chunk_sources[idx]}]\n{self.chunks[idx]}\n\n"
        return context.strip()

# Singleton-ish instantiation for easy app-wide usage
def get_rag_store(data_path=None):
    # Ensure this only builds once per process
    if not hasattr(get_rag_store, "store"):
        if data_path is None:
            data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plant_data')
        get_rag_store.store = RAGStore(data_path)
    return get_rag_store.store

if __name__ == "__main__":
    store = RAGStore(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plant_data'))
    print("Testing Query:")
    print(store.retrieve_context("What should I do if the pump bearing fails?"))
