# DocVerse AI

Cost-optimized, citation-aware PDF question answering with Retrieval-Augmented Generation (RAG).

DocVerse AI lets users upload PDF documents and ask questions about their content. It uses local SentenceTransformer embeddings to avoid embedding API costs, Chroma for vector search, FastAPI for the backend API, Streamlit for the interface, and Groq for answer generation.

## Why this project

- Local `sentence-transformers/all-MiniLM-L6-v2` embeddings
- GPU acceleration when CUDA is available, with CPU fallback
- Chroma vector storage and similarity retrieval
- Grounded answers with source document and page citations
- Upload validation and configurable file-size limits
- Duplicate-upload prevention using file hashes
- Streamlit answer caching for repeated questions
- Configurable model, chunking, retrieval, and output-token settings
- Retrieval, groundedness, latency, token, and cost evaluation

## Application flow

```text
Upload PDF in Streamlit
        |
        v
FastAPI validates and stores the file
        |
        v
PDF text is split into chunks
        |
        v
Local SentenceTransformer creates embeddings
        |
        v
Chroma stores and retrieves relevant chunks
        |
        v
Groq generates an answer from retrieved context
        |
        v
Streamlit displays the answer and source pages
```

## Cost optimization

- Embeddings run locally, avoiding a paid embedding API charge.
- Embedding models are cached in memory after the first load.
- Duplicate files are not indexed repeatedly during a Streamlit session.
- Repeated questions can be served from the application cache.
- `MAX_OUTPUT_TOKENS` limits generation cost and response length.
- Token usage and estimated cost are recorded by the RAG evaluation runner.

## Project structure

```text
.
├── app.py                         # Streamlit frontend
├── fast.py                        # FastAPI application and endpoints
├── backend/
│   ├── config.py                  # Environment-backed settings
│   ├── embeddings.py              # Cached local embedding model
│   ├── ingest.py                  # PDF loading, splitting, and indexing
│   ├── retriever.py               # Chroma retrieval
│   └── llm.py                     # Groq generation and usage data
├── evaluation/
│   ├── datasets/unit_ii.jsonl     # Retrieval evaluation questions
│   ├── metrics.py                 # Retrieval and cost metrics
│   ├── run_retrieval.py           # Hit@K and MRR evaluation
│   ├── run_rag.py                 # End-to-end RAG evaluation
│   └── create_groundedness_review.py
├── tests/                         # API tests
├── Unit-II.pdf                    # Sample document
├── requirements.txt
├── .env.example
└── pytest.ini
```

Generated runtime data is stored locally in `uploads/`, `vectorstore/`, and `evaluation/results/`; these directories are ignored by Git.

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

Create the environment file:

```powershell
Copy-Item .env.example .env
```

Set your Groq API key in `.env`:

```env
GROQ_API_KEY=your_groq_api_key
```

Useful settings include:

```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DEVICE=auto
LLM_MODEL=openai/gpt-oss-20b
MAX_OUTPUT_TOKENS=400
CHUNK_SIZE=600
CHUNK_OVERLAP=100
RETRIEVAL_K=3
```

## Run the application

Start FastAPI from the project root:

```powershell
uvicorn fast:app --reload
```

In a second terminal, start Streamlit:

```powershell
streamlit run app.py
```

Open the local Streamlit URL, upload a PDF, and ask a question.

API endpoints:

- `GET /health` — service health check
- `POST /upload` — validate, save, and index a PDF
- `POST /query` — retrieve context and generate an answer

## Index a document manually

The sample ingestion script indexes `Unit-II.pdf`:

```powershell
python -m backend.ingest
```

For a clean evaluation index:

```powershell
$env:VECTORSTORE_DIR="vectorstore/eval_unit_ii"
python -m backend.ingest
python -m evaluation.run_retrieval
Remove-Item Env:VECTORSTORE_DIR
```

Re-index whenever the embedding model, chunking settings, or source corpus changes.

## Evaluation

Run retrieval evaluation:

```powershell
python -m evaluation.run_retrieval
```

This reports Hit@3, MRR, and retrieval latency. Run the end-to-end evaluation with:

```powershell
python -m evaluation.run_rag
```

Results are saved to `evaluation/results/rag_results.jsonl` and include retrieved sources, generated answers, token usage, estimated cost, retrieval latency, generation latency, and total latency.

Create a groundedness review file:

```powershell
python -m evaluation.create_groundedness_review
```

Review each answer against its retrieved context and record a groundedness score in the generated CSV.

## Tests

```powershell
pytest -q
```

The tests cover health checks, upload validation, query validation, and successful query responses.

## Security and repository notes

- Never commit `.env` or API keys.
- Uploaded documents, Chroma databases, caches, and evaluation results are local runtime data.
- The sample `Unit-II.pdf` is used by the current evaluation dataset.
- Run commands from the project root so imports such as `backend.config` resolve correctly.

## Future improvements

- Add authentication and per-user document collections.
- Replace in-process caching with a shared production cache.
- Add reranking and hybrid keyword/vector retrieval.
- Add automated groundedness and answer-quality scoring.
- Add structured logging, monitoring, and tracing.
- Add CI checks and container deployment when requirements are stable.

