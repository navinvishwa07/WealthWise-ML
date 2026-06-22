from functools import lru_cache
import os

import config
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from vector_store import query_similar
from knowledge_base import query_knowledge_base

load_dotenv()

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


@lru_cache(maxsize=1)
def get_chain():
    """Build the Groq-backed LangChain chain lazily."""
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key or api_key == "your_key_here":
        raise RuntimeError("GROQ_API_KEY is not configured. Add it to your .env file.")

    llm = ChatGroq(
        api_key=api_key,
        model_name=config.GROQ_MODEL
    )
    return prompt | llm | StrOutputParser()


def ask_rag(question):
    transactions = query_similar(question, n_results=5)
    knowledge = query_knowledge_base(question, n_results=3)
    
    transaction_context = "\n".join(transactions['documents'][0])
    knowledge_context = "\n".join(knowledge['documents'][0])
    
    return get_chain().invoke({
        "transactions": transaction_context,
        "knowledge": knowledge_context,
        "question": question
    })
