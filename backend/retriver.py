import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
import torch
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv(override=True)

device = "cuda" if torch.cuda.is_available() else "cpu"
embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": device, "local_files_only": True},
    encode_kwargs={"normalize_embeddings": True}
)

def retriever(query):

    vector_store = Chroma(
        persist_directory="./vectorstore/chroma_local_db",
        embedding_function=embedding,
    )

    results = vector_store.as_retriever(search_kwargs={"k": 3}).invoke(query)
    return results


if __name__ == "__main__":
    response = retriever("what is regression")
    print(response)
