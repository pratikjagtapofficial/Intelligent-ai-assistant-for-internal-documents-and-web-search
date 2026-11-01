# Intelligent AI Assistant for Internal Documents and Web Search

A full-stack chat assistant that answers questions about internal company documents and can search the public web for current or external information. The backend uses a LangChain agent with Google Gemini, Exa web search, and a FAISS document index. The frontend is a Next.js chat interface. Users access the application through one frontend port; Next.js proxies API requests to the backend.

## Features

- Search internal PDF, DOCX, and TXT documents using vector retrieval.
- Search the public web with Exa for current or external questions.
- Combine internal policy retrieval and web search when a question needs both.
- Keep chat history in PostgreSQL.
- Render assistant answers as Markdown in the web interface.

## Project structure

```text
PP/
├── Backend/
│   ├── api.py                 # FastAPI endpoints
│   ├── database.py            # PostgreSQL connection and session setup
│   ├── documents/             # Source documents for internal retrieval
│   ├── Faiss_Index/           # Saved FAISS index used by the assistant
│   ├── ingest.py              # Build/rebuild the document index
│   ├── init_db.py             # Create database tables
│   ├── main.py                # Agent, tools, and CLI chat
│   └── models.py              # Conversation and message models
└── Frontend/
    └── src/app/               # Next.js chat interface
```

## Requirements

- Python 3.10 or later
- Node.js and npm
- PostgreSQL
- Google Gemini API key
- Exa API key

The first backend run may download the `BAAI/bge-small-en-v1.5` embedding model.

## Configuration

Create `PP/.env` and set the service credentials and PostgreSQL connection URL:

```dotenv
GEMINI_API_KEY=your_gemini_api_key
EXA_API_KEY=your_exa_api_key
DATABASE_URL=postgresql+psycopg://<user>:<password>@localhost:5432/assistant

# Optional; defaults to the local Next.js development origins.
FRONTEND_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

`GOOGLE_API_KEY` can be used instead of `GEMINI_API_KEY`. Keep `.env` private; do not commit real credentials.

Next.js proxies `/api/*` requests to the backend. To change the backend's private/upstream address, create `PP/Frontend/.env.local`:

```dotenv
BACKEND_API_URL=http://127.0.0.1:8000
```

## Setup and run

### 1. Install backend dependencies

From the repository root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Prepare PostgreSQL

Create a PostgreSQL database matching the database name in `DATABASE_URL`, then initialize the tables:

```powershell
cd PP\Backend
python init_db.py
```

### 3. Start the backend

From `PP\Backend`:

```powershell
uvicorn api:app --reload
```

The backend listens on port `8000` as an internal upstream. Users should access the app and its proxied API through the frontend port only. For local development, the chat UI is at `http://localhost:3000`, while the backend health endpoint and interactive API docs can be reached through `http://localhost:3000/api/health` and `http://localhost:3000/api/docs`.

### 4. Start the frontend

In another terminal, from `PP\Frontend`:

```powershell
npm ci
npm run dev
```

Open `http://localhost:3000` in a browser.

## API

The frontend proxies API requests through its own origin, so the browser uses the same port for both the UI and backend API:

- `GET /api/` — basic backend status
- `GET /api/health` — health check
- `POST /api/chat` — send a chat message

Example request:

```json
{
  "question": "What is our remote work policy?",
  "session_id": "a-unique-conversation-id"
}
```

The chat response includes the question, answer, and tools used by the agent. The backend process uses its own upstream port (`8000` by default), but it is not the port users need to access; the Next.js server exposes both frontend and API on its single port.

## Updating internal documents

1. Add supported `.pdf`, `.docx`, or `.txt` files under `PP/Backend/documents/`.
2. From `PP/Backend`, rebuild the saved FAISS index:

   ```powershell
   python ingest.py
   ```

3. Restart the backend so it loads the updated index.

The index is saved under `PP/Backend/faiss_index` by the ingestion script. The application currently loads the checked-in index from `PP/Backend/Faiss_Index`; after rebuilding, place/use the generated index at that application path if your filesystem treats those directory names as distinct.

## Notes

- The sample documents in this repository are demonstration content. Replace them only with documents you are authorized to process.
- The Gemini and Exa services may have usage limits and require valid API credentials.
- The `Backend/test_*.py` files include tests and service checks; some may need credentials or network access.
