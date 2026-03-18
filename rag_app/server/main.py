import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_service import RAGService
from ollama_client import OllamaClient
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = RAGService()
ollama = OllamaClient(model="gemma3")

class QueryRequest(BaseModel):
    query: str

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        if file.filename.endswith(".pdf"):
            chunks = rag.process_pdf(temp_path)
        else:
            with open(temp_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            chunks = [text[i:i+500] for i in range(0, len(text), 500)]
        rag.ingest_documents(chunks)
        return {"status": "success", "chunks_processed": len(chunks)}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/query")
async def query_rag(request: QueryRequest):
    print(f"Received query: {request.query}")
    docs = rag.search(request.query)
    print(f"Retrieved {len(docs)} context docs")
    context = "\n\n".join(docs)
    prompt = f"Context:\n{context}\n\nQuestion: {request.query}\n\nHint: If the context is empty, tell the user to upload a document."
    system_prompt = "You are a helpful AI assistant. Use the provided context to answer the user's question accurately. If no context is provided, ask the user to upload a document."
    response = ollama.generate_response(prompt, system_prompt)
    return {"answer": response, "sources": docs}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
