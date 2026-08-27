#importing library
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
import sys
from backend.retriver import retriever

from dotenv import load_dotenv
sys.stdout.reconfigure(encoding="utf-8")

# loading env variables
load_dotenv(override=True)


model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_tokens=400)

prompt = PromptTemplate(
    template="""
Answer the question using ONLY the provided context. Answer the question in detail.

Context:
{context}

Question:
{question}
""",
    input_variables=["context", "question"],
)

parser = StrOutputParser()

chain = prompt | model | parser


def chatbot(query,context):
    response = chain.invoke({"context": context, "question": query})
    
    return response


if __name__ == "__main__":
    chatbot()
