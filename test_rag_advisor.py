import importlib.util
import os

from dotenv import load_dotenv


REQUIRED_MODULES = [
    "langchain_groq",
    "langchain_core.prompts",
    "langchain_core.output_parsers",
    "chromadb",
    "sentence_transformers",
]


def module_available(module_name):
    return importlib.util.find_spec(module_name) is not None


def main():
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")

    print("=" * 60)
    print("RAG ADVISOR SMOKE CHECK")
    print("=" * 60)

    for module_name in REQUIRED_MODULES:
        status = "✅" if module_available(module_name) else "❌"
        print(f"{status} {module_name}")

    if not api_key or api_key == "your_key_here":
        print("\n⚠️  GROQ_API_KEY is not configured; live advisor calls will be skipped.")
    else:
        print("\n✅ GROQ_API_KEY loaded successfully.")

    try:
        from rag_advisor import ask_rag

        print("✅ rag_advisor.ask_rag is importable.")
    except ImportError as exc:
        print(f"❌ rag_advisor import failed: {exc}")

    print("=" * 60)


if __name__ == "__main__":
    main()
