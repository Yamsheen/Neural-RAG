import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from app.config import FAISS_INDEX_FILE, CHUNKS_FILE, EMBEDDING_MODEL

# Load model
embedding_model = SentenceTransformer(EMBEDDING_MODEL)

def build_faiss_index(chunks):
    embeddings = embedding_model.encode(chunks, convert_to_numpy=True, show_progress_bar=True)
    dim = embeddings.shape[1]
    
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    
    # Save index and chunks
    os.makedirs(os.path.dirname(FAISS_INDEX_FILE), exist_ok=True)
    faiss.write_index(index, FAISS_INDEX_FILE)
    np.save(CHUNKS_FILE, np.array(chunks))
    return index, embeddings

def load_faiss_index():
    index = faiss.read_index(FAISS_INDEX_FILE)
    chunks = np.load(CHUNKS_FILE, allow_pickle=True).tolist()
    return index, chunks
