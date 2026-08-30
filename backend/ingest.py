
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.config import get_settings
from backend.embeddings import get_embeddings

settings = get_settings()

def document_indexing(file_path):
    
    #Loading PDF
    loader = PyPDFLoader(file_path=file_path)
    documents = loader.load()

    #Splittng the document
    splitter = RecursiveCharacterTextSplitter(chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap)
    chunks = splitter.split_documents(documents)

    #Converting into Embeddings
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings,
        persist_directory=str(settings.vector_store_dir),                                           
    )

    print(vector_store)

if __name__ == "__main__":
    document_indexing("Unit-II.pdf")

