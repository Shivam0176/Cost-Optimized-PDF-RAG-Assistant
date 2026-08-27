import os

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv(override=True)

def document_indexing(file_path):
    google_api_key = os.getenv("GEMINI_API_KEY")
    
    #Loading PDF
    loader = PyPDFLoader(file_path=file_path)
    documents = loader.load()

    #Splittng the document
    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    chunks = splitter.split_documents(documents)

    #Converting into Embeddings
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-2-preview",
            google_api_key=google_api_key,
        ),
        persist_directory="./vectorstore/chroma_langchain_db"                                           
    )

    print(vector_store)

if __name__ == "__main__":
    document_indexing()

