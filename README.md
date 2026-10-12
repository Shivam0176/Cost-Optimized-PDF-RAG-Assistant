# DocVerse AI

**A cost-conscious PDF RAG assistant built to measure retrieval quality, latency, and LLM usage—not just generate answers.**

DocVerse AI lets you upload a PDF, ask questions about its content, and receive an answer with source-page references. It combines local embeddings, Chroma vector search, FastAPI, Streamlit, and Groq for generation.

> This is a learning and evaluation project, not a production-ready multi-user service. See [Known limitations](#known-limitations).

## Why I built it

A basic RAG demo can show that retrieval and generation work. I wanted to understand the trade-offs behind the pipeline: how good retrieval is, how much latency comes from each stage, and how to reduce avoidable API usage.

The project explores:

- **Local embeddings** with `sentence-transformers/all-MiniLM-L6-v2` to avoid embedding API charges.
- **Vector retrieval** using Chroma and configurable chunking and top-k settings.
- **Source references** that return the retrieved PDF filename and page number.
- **In-process caching** for the embedding model and repeated questions in a Streamlit session.
- **Cost and latency measurement** for retrieval and LLM generation.
- **A small evaluation dataset** for tracking retrieval performance as the system changes.

## How it works

```text
Streamlit UI
    │
    ├── Upload PDF ──> FastAPI validates and saves file
    │                         │
    │                         v
    │                 PyPDFLoader extracts pages
    │                         │
    │                         v
    │                 Text splitter creates chunks
    │                         │
    │                         v
    │                 Local embedding model
    │                         │
    │                         v
    │                    Chroma store
    │
    └── Ask question ──> FastAPI
                             │
                             v
                      Retrieve top-k chunks
                             │
                             v
                      Groq LLM generates answer
                             │
                             v
                    Answer + source page references
```

## Tech stack

| Component | Technology | Purpose |
|---|---|---|
| UI | Streamlit | PDF upload and question-answering interface |
| API | FastAPI | Upload, retrieval, and answer endpoints |
| PDF parsing | PyPDFLoader | Extract page text and metadata |
| Text splitting | RecursiveCharacterTextSplitter | Split page text into retrieval chunks |
| Embeddings | Sentence Transformers | Generate local text embeddings |
| Vector database | Chroma | Store and retrieve document chunks |
| Generation | Groq via LangChain | Generate answers from retrieved context |
| Tests | pytest, FastAPI TestClient | Exercise API behavior |

## Evaluation

The project includes a labelled question dataset and scripts for retrieval and end-to-end RAG evaluation.

### Previously recorded baseline

| Metric | Result |
|---|---:|
| Hit@3 | 89.5% |
| Mean Reciprocal Rank (MRR) | 0.763 |
| Warm retrieval latency | ~24 ms |
| Median generation latency | ~5.15 s |
| P95 generation latency | ~10.48 s |
| Estimated average Groq cost per query | ~$0.000163 |

These are baseline measurements from the project's earlier evaluation run, not a guarantee of performance on other documents or hardware. Retrieval latency excludes model cold-start time; LLM latency depends on provider load, model, prompt size, and network conditions. Cost is an estimate based on the pricing assumptions in `evaluation/metrics.py`, so update those assumptions before comparing costs.

### Run the evaluation

The retrieval dataset currently targets the sample `Unit-II.pdf`. Use a clean vector-store directory so old chunks do not affect the result.

PowerShell:

```powershell
$env:VECTORSTORE_DIR = "vectorstore/eval_unit_ii"
python -m backend.ingest
python -m evaluation.run_retrieval
python -m evaluation.run_rag
Remove-Item Env:VECTORSTORE_DIR
```

The scripts report retrieval metrics, latency, token usage, and estimated generation cost. End-to-end results are written to `evaluation/results/rag_results.jsonl`.

For a groundedness review CSV:

```powershell
python -m evaluation.create_groundedness_review
```

Review the generated answers against their retrieved context and record your assessment. The current groundedness workflow involves manual review; it should not be interpreted as an automated factuality score.

## Getting started

### Requirements

- Python 3.10 or a compatible Python version for the installed dependencies
- A Groq API key
- Internet access for Groq requests
- The embedding model downloaded locally before running, because the embedding loader uses `local_files_only=True`
- Optional: CUDA-compatible PyTorch setup if you want GPU embeddings

### 1. Clone and create a virtual environment

```powershell
git clone https://github.com/Shivam0176/Cost-Optimized-PDF-RAG-Assistant.git
cd Cost-Optimized-PDF-RAG-Assistant

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Download the embedding model

Run this once while connected to the internet:

```powershell
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

If you change `EMBEDDING_MODEL`, download that model to the local cache before starting the application.

### 3. Configure environment variables

```powershell
Copy-Item .env.example .env
```

Open `.env` and set your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key
```

Common settings:

| Variable | Default | Description |
|---|---|---|
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Local embedding model |
| `EMBEDDING_DEVICE` | `auto` | `auto`, `cpu`, or `cuda` |
| `LLM_MODEL` | `openai/gpt-oss-20b` | Groq-supported generation model |
| `MAX_OUTPUT_TOKENS` | `400` | Maximum generated tokens |
| `CHUNK_SIZE` | `600` | Text chunk size |
| `CHUNK_OVERLAP` | `100` | Overlap between chunks |
| `RETRIEVAL_K` | `3` | Number of chunks retrieved |
| `MAX_UPLOAD_BYTES` | `209715200` | Maximum accepted upload size in bytes |
| `UPLOAD_DIR` | `uploads` | Uploaded PDF directory |
| `VECTORSTORE_DIR` | `vectorstore/chroma_local_db` | Chroma persistence directory |
| `API_BASE_URL` | `http://127.0.0.1:8000` | FastAPI base URL used by Streamlit |

Do not commit `.env` or expose your API key.

### 4. Start the backend and UI

Terminal 1 — FastAPI:

```powershell
uvicorn fast:app --reload
```

Terminal 2 — Streamlit:

```powershell
streamlit run app.py
```

Open the local URL printed by Streamlit, upload a PDF, and ask a question.

### API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Return basic service status and model configuration |
| `POST` | `/upload` | Save and index a PDF |
| `POST` | `/query` | Retrieve context and generate an answer |

## Tests

Run the current test suite from the project root:

```powershell
pytest -q
```

The existing tests cover basic health, upload/query validation, and a successful query response. They do not yet provide comprehensive coverage for document isolation, duplicate indexing, malformed PDFs, or concurrent requests.

## Repository layout

```text
.
├── app.py
├── fast.py
├── backend/
│   ├── config.py
│   ├── embeddings.py
│   ├── ingest.py
│   ├── llm.py
│   └── retriever.py
├── evaluation/
│   ├── datasets/unit_ii.jsonl
│   ├── metrics.py
│   ├── run_retrieval.py
│   ├── run_rag.py
│   └── create_groundedness_review.py
├── tests/
├── Unit-II.pdf
├── requirements.txt
└── .env.example
```

## Known limitations

- The current vector store is shared. Retrieval is not yet filtered by a selected document or user, so this should not be used for private multi-user documents.
- Duplicate detection in the Streamlit UI is session-local; backend ingestion does not yet enforce content-hash idempotency.
- Upload validation relies on metadata such as MIME type and filename extension. Add content-level validation and robust streaming limits before exposing the API publicly.
- The answer cache is in-process and session-local, not a shared production cache.
- The evaluation set is small and focused on one sample PDF. Results may not generalize to other document types or question distributions.
- Citation references identify retrieved source pages; they do not independently prove that every generated claim is supported by those pages.
- Dependency versions are not currently pinned to a tested lockfile.

## Next steps

- Add document-level isolation and authorization.
- Make ingestion idempotent using content hashes and deterministic chunk IDs.
- Expand evaluation across multiple PDFs and unanswerable questions.
- Compare dense retrieval with hybrid search and reranking.
- Add stronger upload validation, structured logging, CI, and deployment checks.

## Learning notes

This project is an ongoing experiment in building RAG systems with measurable trade-offs. The main lesson so far: retrieval quality, latency, cost, and reliability need to be evaluated together.
