import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv(override=True)


def retriever(query):
    google_api_key = os.getenv("GEMINI_API_KEY")
    if not google_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured. Add it to your local .env file.")

    embedding = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-2-preview",
        google_api_key=google_api_key,
    )

    vector_store = Chroma(
        persist_directory="./vectorstore/chroma_langchain_db",
        embedding_function=embedding,
    )

    docs = vector_store.as_retriever(search_kwargs={"k": 3}).invoke(query)
    return "\n\n".join(doc.page_content for doc in docs)


if __name__ == "__main__":
    print(retriever(query="what is an agent"))
