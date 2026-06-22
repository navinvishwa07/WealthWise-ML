from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from vector_store import query_similar
from knowledge_base import query_knowledge_base
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile"
)

prompt = PromptTemplate.from_template("""
You are WealthWise, a personal finance advisor for Indian students.
Use the following context to answer the question.

Relevant Transactions:
{transactions}

Finance Knowledge:
{knowledge}

Question: {question}

Give specific, actionable advice based on the context above.
""")

chain = prompt | llm | StrOutputParser()

def ask_rag(question):
    transactions = query_similar(question, n_results=5)
    knowledge = query_knowledge_base(question, n_results=3)
    
    transaction_context = "\n".join(transactions['documents'][0])
    knowledge_context = "\n".join(knowledge['documents'][0])
    
    return chain.invoke({
        "transactions": transaction_context,
        "knowledge": knowledge_context,
        "question": question
    })