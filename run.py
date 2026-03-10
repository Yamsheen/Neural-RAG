from app.pdf_processing import pdf_to_chunks
from app.embeddings import build_faiss_index
import os

pdf_path = os.path.join("data", "sample.pdf")
chunks = pdf_to_chunks(pdf_path)
build_faiss_index(chunks)

