import streamlit as st
import os
import requests
from backend.ingest import document_indexing
from backend.retriver import retriever
from backend.llm import chatbot

st.title("DocVerse AI")
st.write("A RAG application that takes PDF document as input and user can ask questions in contex of that document")

# Uploading File
uploaded_file = st.file_uploader(
    "Upload PDF",
    type=['pdf']
)

API_URL = "http://localhost:8000/upload" 


if uploaded_file is not None:
    files = {
        "file":(
            uploaded_file.name,
            uploaded_file.getvalue(),
            "application/pdf"
        )
    }

    try:
        response = requests.post(API_URL,files=files)
        result = response.json
        print(result,"\n")

    except:
        print("error")



    os.makedirs('uploads',exist_ok=True)

    file_path = os.path.join("uploads",uploaded_file.name)

    with open(file_path,'wb') as f:
        f.write(uploaded_file.getbuffer())

    st.success("File Saved Successfullly")
    document_indexing(file_path)



    query = st.text_input("Enter question to ask related to document")

    if st.button("Submit"):
        try:
            response = requests.post(API_URL,query)
            context = retriever(query)
            response = chatbot(query,context)
            st.write(response)


        except:
            st.write("Enter some text")

        
    



