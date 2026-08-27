from fastapi import FastAPI,UploadFile,HTTPException, File
from pydantic import BaseModel,Field


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

    return {
        "message":"Validation Successful",
        "filename":file.filename
    }


#Query endpoint
@app.post('/query')
async def read_query(query: QueryRequest):

    query = query.query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty."
        )

    return "Query Successfull"



