import logging
import os

# 1. Import the tools needed to build our API.
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_google_genai.chat_models import GoogleRateLimitError
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

# 2. Import our existing AI agent.
from database import get_db
from main import agent
from models import Conversation, Message

logger = logging.getLogger(__name__)


# 3. Create the FastAPI application.
app = FastAPI(
    title="AI Agent Platform",
    description="API for our AI agent",
    version="1.0.0",
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# 4. Define the JSON format expected from the frontend.
class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    session_id: str = Field(min_length=1)


# 5. Create a route to check whether the backend is running.
@app.get("/")
def home():
    return {"message": "AI Agent Platform is running"}


# 6. Create a health-check route.
@app.get("/health")
def health_check():
    return {"status": "healthy"}


# 7. Create the chat API endpoint.
@app.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)):

    try:
        conversation = db.get(Conversation, request.session_id)
        history = (
            [
                {"role": message.role, "content": message.content}
                for message in conversation.messages
            ]
            if conversation
            else []
        )

        # Send the previous conversation plus the new question.
        result = agent.invoke({
            "messages": [
                *history,
                {
                    "role": "user",
                    "content": request.question,
                },
            ]
        })

        messages = result.get("messages", [])

        if not messages:
            raise RuntimeError("The agent returned no messages.")

        # The last message contains the final answer.
        content = messages[-1].content

        # Convert the answer into a plain string.
        if isinstance(content, str):
            answer = content

        elif isinstance(content, list):
            answer = "\n".join(
                block.get("text", "")
                for block in content
                if isinstance(block, dict)
                and block.get("type") == "text"
            ).strip()

        else:
            answer = str(content)

        if conversation is None:
            conversation = Conversation(id=request.session_id)
            db.add(conversation)

        conversation.messages.extend(
            [
                Message(
                    role="user",
                    content=request.question,
                ),
                Message(
                    role="assistant",
                    content=answer,
                ),
            ]
        )
        db.commit()

        # Identify which tools the agent requested.
        tools_used = []

        for message in messages:
            for tool_call in getattr(message, "tool_calls", []):
                name = tool_call.get("name")

                if name and name not in tools_used:
                    tools_used.append(name)

        # Return the answer as JSON.
        return {
            "question": request.question,
            "answer": answer,
            "tools_used": tools_used,
        }

    except GoogleRateLimitError as error:
        logger.warning("Gemini request quota exhausted: %s", error)
        raise HTTPException(
            status_code=429,
            detail=(
                "Gemini's daily free-tier request quota has been reached. "
                "Try again after the quota resets or enable billing/increase "
                "the quota in Google AI Studio."
            ),
        ) from error

    except Exception as error:
        logger.exception("Agent request failed")
        raise HTTPException(
            status_code=500,
            detail="The AI agent failed. Check the backend terminal.",
        ) from error