
from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


# Find the folder containing this Python file.
BASE_DIR = Path(__file__).resolve().parent

# Locate the FAISS index created by ingest.py.
FAISS_DIR = BASE_DIR / "faiss_index"


# Step 1: Load the same embedding model used during ingestion.
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)


# Step 2: Load the saved FAISS index.
vectorstore = FAISS.load_local(
    str(FAISS_DIR),
    embeddings,
    allow_dangerous_deserialization=True
)


# Step 3: Ask a question about company policies.
query = "What is the company's leave policy?"


# Step 4: Search for the 3 most relevant document chunks.
documents = vectorstore.similarity_search(
    query,
    k=3
)


# Step 5: Display the retrieved text and its source.
print("\nQuestion:", query)
print("\nRetrieved documents:")

for doc in documents:
    print("\n--- Document ---")
    print("Source:", doc.metadata.get("document_name", "Unknown"))
    print("Content:", doc.page_content)
