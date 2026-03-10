# # app/pdf_processor.py

# import os
# import uuid
# import numpy as np
# from typing import List
# from PyPDF2 import PdfReader
# from langchain.text_splitter import CharacterTextSplitter

# # Import embedding model and vectorstore from rag_pipeline
# from app.rag_pipeline import embedding_model, vectorstore, CHUNKS_FILE, INDEX_DIR, INDEX_NAME

# # Directory to store uploaded PDFs
# UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "../uploaded_pdfs")
# os.makedirs(UPLOAD_DIR, exist_ok=True)


# def save_pdf(file_bytes: bytes, filename: str = None) -> str:
#     """
#     Save uploaded PDF to disk with unique filename.
#     Returns the saved file path.
#     """
#     if not filename:
#         filename = f"{uuid.uuid4()}.pdf"
#     file_path = os.path.join(UPLOAD_DIR, filename)
#     with open(file_path, "wb") as f:
#         f.write(file_bytes)
#     return file_path


# def extract_text_from_pdf(pdf_path: str) -> str:
#     """
#     Extracts all text from a PDF file.
#     """
#     reader = PdfReader(pdf_path)
#     text = ""
#     for page in reader.pages:
#         text += page.extract_text() + "\n"
#     return text.strip()


# def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
#     """
#     Split text into chunks for vectorization.
#     """
#     splitter = CharacterTextSplitter(
#         separator="\n",
#         chunk_size=chunk_size,
#         chunk_overlap=overlap,
#         length_function=len
#     )
#     return splitter.split_text(text)


# def process_uploaded_pdf(file_bytes: bytes, filename: str = None) -> int:
#     """
#     Full pipeline:
#     - Save PDF
#     - Extract text
#     - Chunk text
#     - Embed chunks and update FAISS index
#     Returns number of new chunks added.
#     """
#     # 1. Save PDF
#     pdf_path = save_pdf(file_bytes, filename)
#     print(f"[DEBUG] Saved PDF to {pdf_path}")

#     # 2. Extract text
#     text = extract_text_from_pdf(pdf_path)
#     if not text:
#         print("[WARNING] PDF has no extractable text.")
#         return 0

#     # 3. Chunk text
#     new_chunks = chunk_text(text)
#     print(f"[DEBUG] PDF split into {len(new_chunks)} chunks")

#     # 4. Update FAISS index
#     if new_chunks:
#         vectorstore.add_texts(new_chunks, embedding=embedding_model)
#         # Save updated index
#         vectorstore.save_local(INDEX_DIR, index_name=INDEX_NAME)
#         # Update chunks.npy
#         if os.path.exists(CHUNKS_FILE):
#             existing_chunks = np.load(CHUNKS_FILE, allow_pickle=True).tolist()
#         else:
#             existing_chunks = []
#         existing_chunks.extend(new_chunks)
#         np.save(CHUNKS_FILE, np.array(existing_chunks, dtype=object))
#         print(f"[DEBUG] FAISS index updated with {len(new_chunks)} new chunks")

#     return len(new_chunks)


# app/pdf_processor.py

import os
import uuid
import numpy as np
from typing import List, Dict
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter

from app.rag_pipeline import embedding_model, vectorstore, CHUNKS_FILE, INDEX_DIR, INDEX_NAME

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "../uploaded_pdfs")
os.makedirs(UPLOAD_DIR, exist_ok=True)


SECTION_HEADERS = [
    "abstract",
    "introduction",
    "method",
    "methods",
    "dataset",
    "experiments",
    "results",
    "discussion",
    "limitations",
    "conclusion"
]


def save_pdf(file_bytes: bytes, filename: str = None) -> str:
    if not filename:
        filename = f"{uuid.uuid4()}.pdf"

    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    return file_path


def extract_text_with_pages(pdf_path: str) -> List[Dict]:
    """
    Extract text while keeping page numbers.
    """
    reader = PdfReader(pdf_path)

    pages = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text()

        if text:
            pages.append({
                "page": i + 1,
                "text": text
            })

    return pages


def detect_section(text: str) -> str:
    """
    Detect research paper section from chunk.
    """
    lower = text.lower()

    for header in SECTION_HEADERS:
        if header in lower[:200]:
            return header

    return "general"


def chunk_pages(pages: List[Dict], paper_title: str) -> List[Dict]:

    splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len
    )

    chunks = []

    for page in pages:

        page_chunks = splitter.split_text(page["text"])

        for chunk in page_chunks:

            section = detect_section(chunk)

            chunks.append({
                "text": chunk,
                "paper_title": paper_title,
                "page": page["page"],
                "section": section
            })

    return chunks


def process_uploaded_pdf(file_bytes: bytes, filename: str = None) -> int:

    pdf_path = save_pdf(file_bytes, filename)
    print(f"[DEBUG] Saved PDF to {pdf_path}")

    pages = extract_text_with_pages(pdf_path)

    if not pages:
        print("[WARNING] No text extracted.")
        return 0

    paper_title = os.path.basename(pdf_path)

    chunks = chunk_pages(pages, paper_title)

    print(f"[DEBUG] Created {len(chunks)} research chunks")

    texts = [c["text"] for c in chunks]
    metadatas = [
        {
            "paper_title": c["paper_title"],
            "page": c["page"],
            "section": c["section"]
        }
        for c in chunks
    ]

    vectorstore.add_texts(texts=texts, metadatas=metadatas, embedding=embedding_model)

    vectorstore.save_local(INDEX_DIR, index_name=INDEX_NAME)

    if os.path.exists(CHUNKS_FILE):
        existing = np.load(CHUNKS_FILE, allow_pickle=True).tolist()
    else:
        existing = []

    existing.extend(chunks)

    np.save(CHUNKS_FILE, np.array(existing, dtype=object))

    print(f"[DEBUG] Index updated with research metadata")

    return len(chunks)