from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def pdf_to_chunks(pdf_path, chunk_size=1000, chunk_overlap=200):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_text(text)
    return chunks
