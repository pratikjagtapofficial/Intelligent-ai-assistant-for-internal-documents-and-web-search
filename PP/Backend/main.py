# Step 1: Create Virtual Environment
# python -m venv venv

# Step 2: Activate Virtual Environment
# venv\Scripts\activate

# Step 3: Install Required Libraries
# pip install -r requirements.txt

# Step 4: Set Environment Variables
# Create a .env file:
# GOOGLE_API_KEY=your_google_api_key
# EXA_API_KEY=your_tavily_api_key

# Step 5: Import Required Libraries
import os
from pathlib import Path

from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain.agents import create_agent

from langchain_exa import ExaSearchResults

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError(
        f"Gemini API key not found. Set GOOGLE_API_KEY or GEMINI_API_KEY "
        f"in {PROJECT_ROOT / '.env'}."
    )

if not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = api_key

#Step 6: Connect to embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)

#Step 7: Load FAISS Vector Store
# Get the folder containing this main.py file.
BASE_DIR = Path(__file__).resolve().parent

# Build the path to the FAISS index folder.
FAISS_DIR = BASE_DIR / "Faiss_Index"

# Load the saved FAISS index.
vectorstore = FAISS.load_local(
    str(FAISS_DIR),
    embeddings,
    allow_dangerous_deserialization=True
)

#Step 8: Create Retriever from FAISS
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 5}
)



# Step 9: Create a Web Search Tool
# """ Here 2 types of creating tool either manually using @tool decorator or using langchains existing tool
#     if it is available in langchain"""

# method 1: Using langchain existing tool
web_search = ExaSearchResults(
    name="web_search",
    description=(
        "Search the public web for current information, "
        "news, regulations, and external facts."
    )
)

# Method 2: Using @tool decorator
@tool
def search_company_policy(query: str) -> str:
    """Search the company's internal policies."""
    
    docs = retriever.invoke(query)

    return "\n\n".join(
        doc.page_content for doc in docs
    )

# Step 10: Create a llm Model
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    google_api_key=api_key,
    max_output_tokens=1024
)

# Step 11: Create Tool-Calling Agent
agent = create_agent(
    model=llm,
    tools=[
        web_search, 
        search_company_policy
        ],
    system_prompt="""
    You are a helpful company information assistant.

    Use search_company_policy when the question requires
    information from internal company policies.

    Use web_search when the question requires current or
    external internet information.

    When a question requires both internal company policy
    and current internet information, use BOTH tools.

    Clearly distinguish company policy information from
    external web information in your answer.
    """
)

# Step 12: Run the Agent/Chat loop
if __name__ == "__main__":

    while True:

        user_input = input("User: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        response = agent.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        })

        print("\nAgent:", response["messages"][-1].content)