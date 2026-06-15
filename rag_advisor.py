from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from vector_store import query_similar
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile"
)

prompt = PromptTemplate.from_template("""
You are WealthWise, a personal finance advisor for Indian students.
Use the following relevant transactions to answer the question.

Relevant Transactions:
{context}

Question: {question}

Give specific, actionable advice based on the transactions above.
""")

chain = prompt | llm | StrOutputParser()

def ask_rag(question):
    results = query_similar(question, n_results=5)
    context = "\n".join(results['documents'][0])
    return chain.invoke({"context": context, "question": question})
