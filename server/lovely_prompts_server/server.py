from typing import List, Dict, Optional
from pydantic import BaseModel

from fastapi import Depends, FastAPI, HTTPException, WebSocket, Request, WebSocketException, status, Query
from starlette.middleware.base import BaseHTTPMiddleware

from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
import logging

from .db.local import Base, ChatPromptSchema, ChatResponseSchema
from .models import (
    ChatPrompt,
    ChatResponse,
    CompletionPrompt,
    CompletionResponse,
    ChatPromptModel,
    ChatResponseModel,
    CompletionPromptModel,
    CompletionResponseModel,
    ServerChatPromptModel,
    ServerChatResponseModel,
    ServerCompletionPromptModel,
    ServerCompletionResponseModel,
    WSMessage,
)



app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from .body_logging import BodyLoggingMiddleware

app.add_middleware(BodyLoggingMiddleware)


from .lifetime import register_startup_event

register_startup_event(app)

from .common import TAG_API


@app.get("/version/", tags=[TAG_API])
def get_version() -> str:
    from . import version
    return f"Local Lovely Prompts Server version {version}"


from .api.projects import router as projects_router
from .api.updates import router as updates_router
from .api.chat_prompts import router as chat_prompts_router
from .api.chat_responses import router as chat_responses_router
# from .api.completion_prompts import router as completion_prompts_router
# from .api.completion_responses import router as completion_responses_router


app.include_router(projects_router)
app.include_router(updates_router)
app.include_router(chat_prompts_router)
app.include_router(chat_responses_router)


# app.include_router(completion_prompts_router)
# app.include_router(completion_responses_router)

