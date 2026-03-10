# pdf_chunking.py
import os
import glob
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader

INDEX_DIR = os.path.join(os.path.dirname(__file__), "../index")
CHUNKS_FILE = os.path.join(INDEX_DIR, "chunks.npy")
os.makedirs(INDEX_DIR, exist_ok=True)

# Folder where your PDFs are stored
PDF_DIR = os.path.join(os.path.dirname(__file__), "../data")  # create a pdfs folder and add PDFs
pdf_files = glob.glob(os.path.join(PDF_DIR, "*.pdf"))

all_chunks = []

for pdf_file in pdf_files:
    loader = PyPDFLoader(pdf_file)
    docs = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )
    
    for doc in docs:
        chunks = splitter.split_text(doc.page_content)
        all_chunks.extend(chunks)

# Save chunks
np.save(CHUNKS_FILE, np.array(all_chunks, dtype=object))
print(f"[INFO] Saved {len(all_chunks)} chunks to {CHUNKS_FILE}")
