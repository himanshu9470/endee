# AI-Powered RAG Chatbot: Backend (FastAPI) 🐍

This folder contains the backend services for the AI-Powered RAG Chatbot. It manages document processing, vector storage in Endee, and LLM communication.

## 📁 Project Structure
- `main.py`: Entry point for the FastAPI server.
- `rag_service.py`: Service for PDF parsing, text chunking, and Endee DB integration.
- `ollama_client.py`: Client for interacting with the locally hosted Gemma 3 model.
- `requirements.txt`: Python package dependencies.

## ⚙️ Technical Highlights
- **Vector DB**: Endee (High-performance C++ DB)
- **Local LLM**: Gemma 3 via Ollama
- **Embedding**: `all-MiniLM-L6-v2` (384 Dimensions)
- **API Architecture**: RESTful API with MsgPack serialization for high-performance data transfer.

## 🚀 Setup
1. Ensure the virtual environment is activated:
   ```bash
   .\venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the server:
   ```bash
   python main.py
   ```
   *Backend will be available at http://localhost:8000*
