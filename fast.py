from fastapi import FastAPI,UploadFile,HTTPException, File
from pydantic import BaseModel,Field
from backend.retriver import retriever
from backend.llm import chatbot
from pathlib import Path
from backend.ingest import document_indexing


app = FastAPI()


#Query Validation
class QueryRequest(BaseModel):
    query: str = Field(
        min_length=3,
        max_length=500
    )


#Validating uploaded pdf
MAX_FILE_SIZE = 200*1024*1024

async def validate_pdf(file: UploadFile):

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

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400,detail="File size exceeds 200 MB")

    await file.seek(0)


#Document upload endpoint
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    #validate file
    await validate_pdf(file)

    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)

    filename = Path(file.filename).name
    file_path = upload_dir / filename

    with open(file_path,"wb") as saved_file:
        saved_file.write(await file.read())

    document_indexing(str(file_path))

    return {
        "message": "File indexed successfully",
        "filename": filename
    }


#Query endpoint
@app.post('/query')
async def read_query(request: QueryRequest):
    question = request.query.strip()

    docs = retriever(question)

    if not docs:
        raise HTTPException(
            status_code=404,
            detail="No relevant information was found in the indexed documents."
        )

    context = "\n\n".join(doc.page_content for doc in docs)
    answer = chatbot(question,context)

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



