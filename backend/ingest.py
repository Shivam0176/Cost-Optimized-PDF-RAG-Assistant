import os

from langchain_chroma import Chroma
import torch
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv(override=True)

device = "cuda" if torch.cuda.is_available() else "cpu"
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": device, "local_files_only": True},
    encode_kwargs={"normalize_embeddings": True}
)

def document_indexing(file_path):
    
    #Loading PDF
    loader = PyPDFLoader(file_path=file_path)
    documents = loader.load()

    #Splittng the document
    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    chunks = splitter.split_documents(documents)

    #Converting into Embeddings
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./vectorstore/chroma_local_db"                                           
    )

    print(vector_store)

if __name__ == "__main__":
    document_indexing("Unit-II.pdf")

