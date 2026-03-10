import os
import numpy as np
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader

# --------------------------
# CONFIG / PATHS
# --------------------------
PDF_FOLDER = "data"
INDEX_DIR = "index"
CHUNKS_FILE = os.path.join(INDEX_DIR, "chunks.npy")
FAISS_FILE = os.path.join(INDEX_DIR, "pdf_index.faiss")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# --------------------------
# ENSURE INDEX FOLDER EXISTS
# --------------------------
print(f"[DEBUG] INDEX_DIR: {INDEX_DIR}")
os.makedirs(INDEX_DIR, exist_ok=True)
print("[DEBUG] Index folder checked/created.")

# --------------------------
# LOAD PDFs AND CREATE CHUNKS
# --------------------------
all_chunks = []

if not os.path.exists(PDF_FOLDER):
    raise FileNotFoundError(f"[ERROR] PDF folder not found: {PDF_FOLDER}")

pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf")]
print(f"[DEBUG] PDF files found: {pdf_files}")

if not pdf_files:
    raise ValueError("[ERROR] No PDF files found in folder!")

for file in pdf_files:
    file_path = os.path.join(PDF_FOLDER, file)
    print(f"[DEBUG] Loading PDF: {file_path}")
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    print(f"[DEBUG] {len(docs)} pages loaded from {file}")
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    print(f"[DEBUG] {len(chunks)} chunks created from {file}")
    
    all_chunks.extend(chunks)

print(f"[DEBUG] Total chunks created: {len(all_chunks)}")

if len(all_chunks) == 0:
    raise ValueError("[ERROR] No chunks created! Check your PDFs.")

# --------------------------
# SAVE CHUNKS
# --------------------------
np.save(CHUNKS_FILE, np.array(all_chunks, dtype=object))
print(f"[DEBUG] Chunks saved to {CHUNKS_FILE}")

# --------------------------
# INITIALIZE EMBEDDINGS
# --------------------------
print(f"[DEBUG] Initializing embedding model: {EMBEDDING_MODEL}")
embedding_model = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL)
print("[DEBUG] Embedding model initialized.")

# --------------------------
# CREATE OR LOAD FAISS INDEX
# --------------------------
if os.path.exists(FAISS_FILE):
    print(f"[DEBUG] FAISS index exists: {FAISS_FILE}")
    try:
        vectorstore = FAISS.load_local(INDEX_DIR, embedding_model, allow_dangerous_deserialization=True)
        print("[DEBUG] FAISS index loaded successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to load FAISS index: {e}")
        print("[DEBUG] Recreating FAISS index from chunks...")
        vectorstore = FAISS.from_documents(all_chunks, embedding_model)
        vectorstore.save_local(INDEX_DIR)
        print("[DEBUG] FAISS index recreated and saved.")
else:
    print("[DEBUG] No FAISS index found. Creating new index from chunks...")
    vectorstore = FAISS.from_documents(all_chunks, embedding_model)
    vectorstore.save_local(INDEX_DIR)
    print("[DEBUG] FAISS index created and saved.")

print("[INFO] Index building complete. Ready for RAG pipeline.")