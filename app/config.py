import os

# Paths
PDF_DIR = os.path.join(os.path.dirname(__file__), "../data")
INDEX_DIR = os.path.join(os.path.dirname(__file__), "../index")
CHUNKS_FILE = os.path.join(INDEX_DIR, "chunks.npy")
FAISS_INDEX_FILE = os.path.join(INDEX_DIR, "pdf_index.faiss")

# Embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# LLM settings
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
