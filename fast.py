from fastapi import FastAPI,UploadFile,HTTPException, File
from pydantic import BaseModel,Field
from backend.retriever import retriever
from backend.llm import chatbot
from pathlib import Path
from backend.ingest import document_indexing
from backend.config import get_settings
from backend.embeddings import resolve_device
import logging
from contextlib import asynccontextmanager
from starlette.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    settings.upload_dir.mkdir(parents=True,exist_ok=True)
    settings.vectorstore_dir.parent.mkdir(parents=True,exist_ok=True)

    logger.info(
        "API started with embedding_model=%s, embedding_device=%s, llm_model=%s",
        settings.embedding_model,
        resolve_device(),
        settings.llm_model
    )

    yield

    logger.info("API stopped")

app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health_check():
    settings = get_settings()
    return {
        "status": "ok",
        "service": "docverse-api",
        "embedding_device": resolve_device(),
        "llm_model": settings.llm_model
    }


#Query Validation
class QueryRequest(BaseModel):
    query: str = Field(
        min_length=3,
        max_length=500
    )


#Validating uploaded pdf
async def validate_pdf(file: UploadFile):
    settings = get_settings()

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only pdf files are allowed."
        )

    #checking extension
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file extension"
        )

    contents = await file.read()

    if len(contents) > settings.max_upload_bytes:
        raise HTTPException(status_code=400,detail="File size exceeds 200 MB")

    await file.seek(0)


#Document upload endpoint
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    #validate file
    await validate_pdf(file)
    settings = get_settings()

    upload_dir = settings.upload_dir
    upload_dir.mkdir(parents=True,exist_ok=True)

    filename = Path(file.filename).name
    file_path = upload_dir / filename

    with open(file_path,"wb") as saved_file:
        saved_file.write(await file.read())

    try:
        await run_in_threadpool(document_indexing,str(file_path))
    except Exception:
        logger.exception("document_indexing_failed filename=%s",filename)
        raise HTTPException(
            status_code=500,
            detail="The PDF could not be indexed. Please try another file."
        )

    return {
        "message": "File indexed successfully",
        "filename": filename
    }


#Query endpoint
@app.post('/query')
async def read_query(request: QueryRequest):
    question = request.query.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail="Query cannot contain only spaces."
        )

    try:
        docs = await run_in_threadpool(retriever,question)
    except Exception:
        logger.exception("retrieval_failed")
        raise HTTPException(
            status_code=503,
            detail="Document search is temporarily unavailable."
        )

    if not docs:
        raise HTTPException(
            status_code=404,
            detail="No relevant information was found in the indexed documents."
        )

    context = "\n\n".join(doc.page_content for doc in docs)

    try:
        answer = await run_in_threadpool(chatbot,question,context)
    except Exception:
        logger.exception("answer_generation_failed")
        raise HTTPException(
            status_code=503,
            detail="Answer generation is temporarily unavailable."
        )

    sources = [
        {
            "filename": doc.metadata.get("source","Unknown file"),
            "page": doc.metadata.get("page",0)+1,
        }
        for doc in docs
    ]

    return {
        "answer": answer,
        "sources": sources
    }



