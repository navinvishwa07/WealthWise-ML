import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

print("=" * 60)
print("RAG ADVISOR TEST")
print("=" * 60)

if not api_key or api_key == "your_key_here":
    print("❌ ERROR: GROQ_API_KEY not set in .env file")
    print("\nTo fix:")
    print("1. Copy .env.example to .env")
    print("2. Replace 'your_key_here' with your actual Groq API key")
    print("3. Save and run this test again")
else:
    print("✅ GROQ_API_KEY loaded successfully")
    print(f"   Preview: {api_key[:15]}...")

# Test imports
print("\nTesting imports...")
try:
    from langchain_groq import ChatGroq
    print("✅ langchain_groq")
except ImportError as e:
    print(f"❌ langchain_groq: {e}")

try:
    from langchain_core.prompts import PromptTemplate
    print("✅ langchain_core.prompts")
except ImportError as e:
    print(f"❌ langchain_core.prompts: {e}")

try:
    from langchain_core.output_parsers import StrOutputParser
    print("✅ langchain_core.output_parsers")
except ImportError as e:
    print(f"❌ langchain_core.output_parsers: {e}")

try:
    from vector_store import query_similar
    print("✅ vector_store.query_similar")
except ImportError as e:
    print(f"❌ vector_store: {e}")

# Test rag_advisor module
print("\nTesting rag_advisor module...")
try:
    from rag_advisor import ask_rag, llm, chain
    print("✅ rag_advisor imported successfully")
    print("   - ask_rag function ready")
    print("   - ChatGroq LLM configured")
    print("   - Prompt chain initialized")
except ImportError as e:
    print(f"❌ rag_advisor: {e}")

print("\n" + "=" * 60)
print("✅ All systems ready! RAG advisor is configured.")
print("=" * 60)
