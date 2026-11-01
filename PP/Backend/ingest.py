
from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
)

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


# Find the folder containing this Python file.
BASE_DIR = Path(__file__).resolve().parent

# Folder containing our company documents.
DOCUMENTS_DIR = BASE_DIR / "documents"

# Folder where FAISS will save the index.
FAISS_DIR = BASE_DIR / "faiss_index"


def load_documents():

    # We will collect all loaded documents here.
    documents = []

    # Check that our documents folder exists.
    if not DOCUMENTS_DIR.is_dir():
        print(f"Documents folder not found: {DOCUMENTS_DIR}")
        return documents

    # Search the documents folder and all its subfolders.
    for file_path in DOCUMENTS_DIR.rglob("*"):

        # Ignore folders; process only files.
        if not file_path.is_file():
            continue

        # Get the file extension, such as .pdf or .txt.
        suffix = file_path.suffix.lower()

        try:

            # Load PDF files.
            if suffix == ".pdf":
                loader = PyPDFLoader(str(file_path))

            # Load Word documents.
            elif suffix == ".docx":
                loader = Docx2txtLoader(str(file_path))

            # Load text files.
            elif suffix == ".txt":
                loader = TextLoader(
                    str(file_path),
                    encoding="utf-8"
                )

            # Ignore other file types.
            else:
                print(f"Skipping unsupported file: {file_path}")
                continue

            # Extract text from the file.
            docs = loader.load()

            # Attach useful information to each document.
            for doc in docs:
                doc.metadata["document_name"] = file_path.name
                doc.metadata["file_type"] = suffix

            # Add these documents to our main list.
            documents.extend(docs)

            print(f"Loaded: {file_path}")

        except Exception as e:
            # Report errors without stopping the entire process.
            print(f"Error loading {file_path}: {e}")

    return documents


def main():

    print("Loading documents...")

    # Step 1: Read the files.
    documents = load_documents()

    if not documents:
        print("No documents were loaded. Check the documents folder.")
        return

    print(f"Loaded {len(documents)} document sections.")

    # Step 2: Split the text into smaller chunks.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = text_splitter.split_documents(documents)

    print(f"Created {len(chunks)} chunks.")

    # Step 3: Create the embedding model.
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5"
    )

    # Step 4: Convert the chunks into vectors
    # and build the FAISS index.
    vectorstore = FAISS.from_documents(
        chunks,
        embeddings
    )

    # Step 5: Save the index for future use.
    vectorstore.save_local(str(FAISS_DIR))

    print("FAISS index created successfully.")
    print(f"Saved to: {FAISS_DIR}")


# Run main() only when this file is executed directly.
if __name__ == "__main__":
    main()
