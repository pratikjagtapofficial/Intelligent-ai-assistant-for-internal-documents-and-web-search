
from pathlib import Path
from dotenv import load_dotenv

from langchain_core.tools import tool
from langchain_exa import ExaSearchResults
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


# Find this file's folder.
BASE_DIR = Path(__file__).resolve().parent

# Load API keys from .env.
load_dotenv()

# -----------------------------
# 1. Set up the FAISS retriever
# -----------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)

vectorstore = FAISS.load_local(
    str(BASE_DIR / "faiss_index"),
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = vectorstore.as_retriever(
    search_kwargs={"k": 3}
)


# -----------------------------
# 2. Define the company tool
# -----------------------------

@tool
def search_company_policy(query: str) -> str:
    """Search internal company policies and documents."""

    # Retrieve relevant document chunks from FAISS.
    docs = retriever.invoke(query)

    if not docs:
        return "No relevant company documents found."

    # Combine retrieved text and source filenames.
    results = []

    for doc in docs:
        source = doc.metadata.get(
            "document_name", "Unknown"
        )

        results.append(
            f"Source: {source}\n{doc.page_content}"
        )

    return "\n\n".join(results)


# -----------------------------
# 3. Set up the Exa web tool
# -----------------------------

web_search = ExaSearchResults(
    name="web_search",
    description="Search the public web for relevant information."
)


# -----------------------------
# 4. Test both tools separately
# -----------------------------

if __name__ == "__main__":

    print("\n===== TEST 1: COMPANY POLICY =====")

    policy_result = search_company_policy.invoke({
        "query": "How many annual leave days do employees receive?"
    })

    print(policy_result)

    print("\n===== TEST 2: EXA WEB SEARCH =====")

    web_result = web_search.invoke({
        "query": "Python official documentation",
        "num_results": 3
    })

    print(web_result)