# DocVerse AI

A cost-optimized Retrieval-Augmented Generation (RAG) application for asking questions about uploaded PDF documents.

## How it works

1. Upload a PDF through Streamlit.
2. FastAPI validates, saves, splits, and indexes the document.
3. A local SentenceTransformer model creates embeddings using the GPU when available.
4. Chroma stores and retrieves relevant document chunks.
5. Groq generates a grounded answer with source pages.
6. Repeated questions are served from a Streamlit cache.

## Cost optimization

- Local `all-MiniLM-L6-v2` embeddings replace paid embedding APIs.
- GPU is used automatically when CUDA is available.
- PDF file hashes prevent repeated indexing within a Streamlit session.
- Repeated questions use an answer cache.
- Groq answers are limited to 400 output tokens.

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create your local environment file:

```powershell
Copy-Item .env.example .env
```

Add your Groq API key to `.env`:

```env
GROQ_API_KEY=your_key_here
```

## Run the application

Start FastAPI in one terminal:

```powershell
uvicorn fast:app --reload
```

Start Streamlit in another terminal:

```powershell
streamlit run app.py
```

Open the Streamlit URL shown in the terminal, upload a PDF, and ask a question.

## Project structure

- `app.py` - Streamlit user interface
- `fast.py` - FastAPI upload and query endpoints
- `backend/ingest.py` - PDF loading, chunking, and local embedding
- `backend/retriever.py` - Chroma similarity search
- `backend/llm.py` - Groq answer generation

## Notes

- `uploads/` and `vectorstore/` are generated locally and are intentionally not committed.
- `.env` must never be committed.
- `Unit-II.pdf` is included as a sample document.
