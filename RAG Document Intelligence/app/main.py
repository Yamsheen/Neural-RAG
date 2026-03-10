

# # # app/main.py
# # from fastapi import FastAPI, UploadFile, File, Query
# # from fastapi.responses import StreamingResponse, FileResponse
# # from fastapi.staticfiles import StaticFiles
# # from app.rag_pipeline import qa_chain
# # from app.pdf_processor import process_uploaded_pdf
# # import os

# # app = FastAPI(title="RAG Document Chatbot")

# # # --- FIX: SERVE FRONTEND ---
# # # 1. Map the root URL (/) to your index.html
# # @app.get("/")
# # async def read_index():
# #     # This assumes your index.html is in a folder named 'frontend' at the root
# #     return FileResponse(os.path.join("frontend", "index.html"))

# # # 2. Mount the 'frontend' folder to serve styles.css and app.js
# # # This makes them available at http://127.0.0.1:8000/styles.css etc.
# # app.mount("/", StaticFiles(directory="frontend"), name="static")

# # # -------------------- Upload PDF --------------------
# # @app.post("/upload")
# # async def upload_pdf(file: UploadFile = File(...)):
# #     if not file.filename.lower().endswith(".pdf"):
# #         return {"error": "Only PDF files are supported."}
# #     try:
# #         file_bytes = await file.read()
# #         # Ensure process_uploaded_pdf is imported correctly from your processor
# #         new_chunks_count = process_uploaded_pdf(file_bytes, file.filename)
# #         return {
# #             "message": f"PDF uploaded successfully. {new_chunks_count} chunks added to index."
# #         }
# #     except Exception as e:
# #         return {"error": f"Failed to process PDF: {str(e)}"}

# # # -------------------- Query --------------------
# # @app.get("/query")
# # async def query(q: str = Query(..., description="Question to ask the documents")):
# #     async def answer_stream():
# #         if not q.strip():
# #             yield "[ERROR] Empty question."
# #             return
# #         try:
# #             # invoke() is the standard method for LangChain chains
# #             output = qa_chain.invoke({"query": q})
# #             answer = output.get("result", "")
# #             if not answer:
# #                 yield "[No answer generated]"
# #             else:
# #                 yield answer
# #         except Exception as e:
# #             yield f"[ERROR generating answer: {str(e)}]"
            
# #     return StreamingResponse(answer_stream(), media_type="text/plain")



# # app/main.py

# from fastapi import FastAPI, UploadFile, File, Query
# from fastapi.responses import StreamingResponse, FileResponse
# from fastapi.staticfiles import StaticFiles

# from app.rag_pipeline import query_documents
# from app.pdf_processor import process_uploaded_pdf

# import os

# app = FastAPI(title="AI Research Paper Assistant")


# @app.get("/")
# async def read_index():
#     return FileResponse(os.path.join("frontend", "index.html"))


# app.mount("/", StaticFiles(directory="frontend"), name="static")


# @app.post("/upload")
# async def upload_pdf(file: UploadFile = File(...)):

#     if not file.filename.lower().endswith(".pdf"):
#         return {"error": "Only PDF files supported"}

#     file_bytes = await file.read()

#     chunks = process_uploaded_pdf(file_bytes, file.filename)

#     return {"message": f"{chunks} research chunks indexed"}


# @app.get("/query")
# async def query(q: str = Query(...)):

#     async def answer_stream():

#         result = query_documents(q)

#         yield result["answer"]

#         yield "\n\nSources:\n"

#         for s in result["sources"]:
#             yield f"{s['paper_title']} | Page {s['page']} | Section {s['section']}\n"

#     return StreamingResponse(answer_stream(), media_type="text/plain")


# app/main.py

from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.pdf_processor import process_uploaded_pdf
from app.rag_pipeline import query_documents
import os

app = FastAPI(title="RAG Document Chatbot")

# -------------------- Upload PDF --------------------
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        return {"error": "Only PDF files are supported."}
    try:
        file_bytes = await file.read()
        new_chunks_count = process_uploaded_pdf(file_bytes, file.filename)
        return {"message": f"PDF uploaded successfully. {new_chunks_count} chunks added to index."}
    except Exception as e:
        return {"error": f"Failed to process PDF: {str(e)}"}


# -------------------- Query --------------------
@app.get("/query")
async def query(q: str = Query(..., description="Question to ask the documents")):
    async def answer_stream():
        if not q.strip():
            yield "[ERROR] Empty question."
            return
        try:
            output = query_documents(q)
            answer = output.get("answer", "")
            if not answer:
                yield "[No answer generated]"
            else:
                yield answer
        except Exception as e:
            yield f"[ERROR generating answer: {str(e)}]"

    return StreamingResponse(answer_stream(), media_type="text/plain")


# -------------------- Serve Frontend --------------------
@app.get("/")
async def read_index():
    # Serve index.html at root
    return FileResponse(os.path.join("frontend", "index.html"))


# Mount static frontend assets **after API routes**
app.mount("/", StaticFiles(directory="frontend"), name="static")
