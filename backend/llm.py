#importing library
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from backend.config import get_settings

settings = get_settings()

model = ChatGroq(
    model=settings.llm_model,
    api_key=settings.groq_api_key,
    temperature=0,
    max_tokens=settings.max_output_tokens)

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

def chatbot_with_usage(query, context):
    message = model.invoke(
        prompt.format(
            context=context,
            question=query
        )
    )

    usage = getattr(message, "usage_metadata",None)

    if not usage:
        usage = message.response_metadata.get("token_usage",{})

    return message.content, usage


if __name__ == "__main__":
    chatbot()
