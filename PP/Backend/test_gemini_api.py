
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Load the API key from .env.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

api_key = (
    os.getenv("GOOGLE_API_KEY")
    or os.getenv("GEMINI_API_KEY")
)

if not api_key:
    raise ValueError("Google API key was not found.")

# Gemini's text-generation API endpoint.
url = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-3.6-flash:generateContent"
)

# Send a simple request to Gemini.
try:
    response = httpx.post(
        url,
        params={"key": api_key},
        json={
            "contents": [
                {
                    "parts": [
                        {
                            "text": "Reply with: Gemini works."
                        }
                    ]
                }
            ]
        },
        timeout=30,
    )

    print("HTTP status:", response.status_code)

    if response.is_success:
        data = response.json()
        answer = data["candidates"][0]["content"]["parts"][0]["text"]
        print("Gemini response:", answer)
    else:
        # Show Google's error without displaying your API key.
        print("API error:", response.text)

except httpx.RequestError as error:
    print("Network request failed:", type(error).__name__)
    print(error)
