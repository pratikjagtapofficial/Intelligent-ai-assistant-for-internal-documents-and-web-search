from pathlib import Path
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


# Find the project root directory.
BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

# Load .env from the project root.
load_dotenv(PROJECT_DIR / ".env")

# Read the Google API key without displaying it.
api_key = (
    os.getenv("GOOGLE_API_KEY")
    or os.getenv("GEMINI_API_KEY")
)

if not api_key:
    raise ValueError(
        "Google API key not found. Check your .env file."
    )

print("API key found: Yes")

# Create the Gemini model.
llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    google_api_key=api_key,
    max_output_tokens=128,
)

# Test a simple model request.
try:
    response = llm.invoke(
        "Reply with exactly: Gemini connection successful."
    )

    print("Gemini connection successful!")
    print("Response:", response.content)

except Exception as error:
    print("Gemini request failed.")
    print("Error type:", type(error).__name__)
    print("Error:", error)