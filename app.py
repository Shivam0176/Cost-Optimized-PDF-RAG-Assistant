import streamlit as st
import hashlib
import os
import requests
from backend.ingest import document_indexing


st.title("DocVerse AI")
st.write("A RAG application that takes PDF document as input and user can ask questions in contex of that document")

if 'indexed_files' not in st.session_state:
    st.session_state.indexed_files = set()

if 'answer_cache' not in st.session_state:
    st.session_state.answer_cache = {}

# Uploading File
uploaded_file = st.file_uploader(
    "Upload PDF",
    type=['pdf']
)

API_URL = "http://localhost:8000/upload" 
QUERY_API_URL = "http://127.0.0.1:8000/query"


if uploaded_file is not None:

    # Converting pdf into hash for duplicate detection
    file_bytes = uploaded_file.getvalue()
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    files = {
        "file":(
            uploaded_file.name,
            file_bytes,
            "application/pdf"
        )
    }

    # try:
    #     response = requests.post(API_URL,files=files)
    #     result = response.json()
    #     print(result,"\n")

    # except:
    #     print("error")



    if file_hash not in st.session_state.indexed_files:
        response = requests.post(API_URL,files=files,timeout=120)
        response.raise_for_status()
        
        st.session_state.indexed_files.add(file_hash)
        st.session_state.answer_cache = {}

        st.success("File indexed successfully")



    else:
        st.info("This file is already indexed in this session.")



    query = st.text_input("Enter question to ask related to document")

    if st.button("Submit"):

        clean_query = query.strip().lower()

        if not clean_query:
            st.warning("Please enter a question.")
        elif clean_query in st.session_state.answer_cache:
            result = st.session_state.answer_cache[clean_query]

            st.info("showing a cached answer.")
            st.write(result["answer"])
            st.caption("Sources: " + " | ".join(result["sources"]))

        else:
            try:
                response = requests.post(
                    QUERY_API_URL,
                    json={"query": query},
                    timeout=60
                )
                response.raise_for_status()

                api_result = response.json()

                sources = [
                    f"{os.path.basename(source['filename'])} - page {source['page']}"
                    for source in api_result['sources']
                ]

                result = {
                    "answer": api_result["answer"],
                    "sources": sources
                }

                st.session_state.answer_cache[clean_query] = result

                st.write(result["answer"])
                st.caption("Sources: " + " | ".join(result["sources"]))

            except Exception as error:
                st.write(f"Something went wrong {error}")

        
    



