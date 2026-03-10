
# app/rag_pipeline.py
import os
import numpy as np
import requests
from typing import Optional, List, Any

print("[DEBUG] Initializing 2026 Resilient RAG Pipeline...")
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.llms.base import LLM

# -------------------- CONFIG --------------------
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
INDEX_DIR       = os.path.join(os.path.dirname(__file__), "../index")
CHUNKS_FILE     = os.path.join(INDEX_DIR, "chunks.npy")
INDEX_NAME      = "index"

# 2026 Recommended: Llama-3.1 is the most stable across all HF Inference Providers
HF_API_TOKEN    = "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"
HF_MODEL_ID     = "meta-llama/Llama-3.1-8B-Instruct" 

os.makedirs(INDEX_DIR, exist_ok=True)

# -------------------- CUSTOM LLM WRAPPER (2026 FINAL) --------------------
class HFInferenceLLM(LLM):
    """
    Final Fix for 2026: Using the correct /v1 base URL.
    This version uses the OpenAI-compatible path supported by all Providers.
    """
    model_id: str = HF_MODEL_ID
    hf_api_token: str = HF_API_TOKEN

    @property
    def _llm_type(self) -> str:
        return "hf_router_v1"

    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs: Any) -> str:
        # THE CRITICAL FIX: The base URL is /v1/chat/completions
        api_url = "https://router.huggingface.co/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.hf_api_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant. Use ONLY the provided context to answer."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 512,
            "temperature": 0.1
        }

        print(f"[DEBUG] POST -> {api_url} (Model: {self.model_id})")
        
        try:
            resp = requests.post(api_url, headers=headers, json=payload, timeout=60)
            
            # If Llama-3.1 is busy, fallback to Qwen-2.5-7B
            if resp.status_code != 200:
                print(f"[WARNING] {self.model_id} status {resp.status_code}. Falling back to Qwen...")
                payload["model"] = "Qwen/Qwen2.5-7B-Instruct"
                resp = requests.post(api_url, headers=headers, json=payload, timeout=60)

            resp.raise_for_status()
            data = resp.json()
            return data['choices'][0]['message']['content']
            
        except Exception as e:
            print(f"[ERROR] Final Connection Error: {e}")
            return f"The AI service is temporarily unavailable. Error: {str(e)}"

# -------------------- PROMPT TEMPLATE --------------------
template = """Use the context below to answer the question. 
Context: {context}

Question: {question}

Answer:"""

QA_PROMPT = PromptTemplate(template=template, input_variables=["context", "question"])

# -------------------- INITIALIZATION --------------------
embedding_model = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL)

if os.path.exists(CHUNKS_FILE):
    vectorstore = FAISS.load_local(
        INDEX_DIR, 
        embedding_model, 
        index_name=INDEX_NAME,
        allow_dangerous_deserialization=True
    )
    print("[INFO] FAISS index loaded.")
else:
    raise FileNotFoundError("Missing chunks.npy. Please re-run your PDF chunker.")

llm = HFInferenceLLM()

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
    return_source_documents=True,
    chain_type_kwargs={"prompt": QA_PROMPT}
)

print("[DEBUG] RAG Pipeline Ready. Successfully migrated to 2026 Router.")


def query_documents(question: str):

    retriever = vectorstore.as_retriever(search_kwargs={"k": 8})

    docs = retriever.get_relevant_documents(question)

    context = ""

    sources = []

    for d in docs:

        meta = d.metadata

        context += f"""
Paper: {meta.get('paper_title')}
Section: {meta.get('section')}
Page: {meta.get('page')}

{d.page_content}

---
"""

        sources.append(meta)

    prompt = QA_PROMPT.format(context=context, question=question)

    answer = llm(prompt)

    return {
        "answer": answer,
        "sources": sources
    }