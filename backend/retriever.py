from backend.config import get_settings
from backend.embeddings import get_embeddings
from langchain_chroma import Chroma

def retriever(query):
    settings = get_settings()

    vector_store = Chroma(
        persist_directory=str(settings.vectorstore_dir),
        embedding_function=get_embeddings(),
    )

    results = vector_store.as_retriever(
        search_kwargs={"k": settings.retrieval_k}
        ).invoke(query)
    return results


if __name__ == "__main__":
    response = retriever("what is regression")
    print(response)
