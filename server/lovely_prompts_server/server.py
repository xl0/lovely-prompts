from typing import List, Dict, Optional
from pydantic import BaseModel

from fastapi import Depends, FastAPI, HTTPException, WebSocket, Request, WebSocketException, status, Query
from starlette.middleware.base import BaseHTTPMiddleware

from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
import logging

from .orm.remote import ServerBase, ServerChatPromptSchema, ServerChatResponseSchema
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

# engine = create_engine("sqlite:///./sql_app.db")
# SessionLocal = sessionmaker(autoflush=True, bind=engine)

app = FastAPI()


from fastapi.middleware.cors import CORSMiddleware

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BodyLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method != "GET":
            body = await request.body()
            print(f"{request.url}: Raw Body: {body.decode()}")

            # create a new stream for the body
            async def mock_receive():
                return {"type": "http.request", "body": body}

            # replace the request's receive function with our mock one
            request._receive = mock_receive
        response = await call_next(request)
        return response


app.add_middleware(BodyLoggingMiddleware)


from contextvars import ContextVar

sessionmakers = ContextVar("sessionmakers", default={})


import appdirs
import os
from pathlib import Path


def project_exists(project):
    app_data_dir = appdirs.user_data_dir("lovely_prompts")
    sqlite_file = f"{app_data_dir}/dbs/{project}.db"
    return os.path.exists(sqlite_file)


def project_create(project: str):
    app_data_dir = Path(appdirs.user_data_dir("lovely_prompts"))
    sqlite_file = app_data_dir / "dbs" / f"{project}.db"
    engine = create_engine(f"sqlite:///{sqlite_file}")
    print(engine.url)

    if not project_exists(project):
        print("Creating new database")
        os.makedirs(app_data_dir / "dbs", exist_ok=True)
        ServerBase.metadata.create_all(bind=engine)
    else:
        print("Database already exists")

    return engine


# @app.on_event("startup")
# def create_default_project():
#     project_create("default")


def check_project_exists(project="default"):
    if not project_exists(project):
        raise HTTPException(status_code=404, detail=f"Project '{project}' not found")


def get_session(project="default"):
    thread_local_sm = sessionmakers.get()
    if project not in thread_local_sm:
        engine = project_create(project)
        thread_local_sm[project] = sessionmaker(autoflush=True, bind=engine)

    db = thread_local_sm[project]()
    try:
        yield db
    finally:
        db.close()


def list_projects():
    app_data_dir = appdirs.user_data_dir("lovely_prompts")
    dbs_dir = f"{app_data_dir}/dbs"
    os.makedirs(dbs_dir, exist_ok=True)
    project_names = os.listdir(dbs_dir)
    return [name.replace(".db", "") for name in project_names]


from collections import defaultdict
import asyncio


event_queues: Dict[str, List[asyncio.Queue]] = defaultdict(list)

from enum import Enum

# Don't forget to sync with the webapp
class UpdateEvents(Enum):
    NEW_CHAT_PROMPT = "new_chp"
    UPDATE_CHAT_PROMPT = "up_chp"
    DELETE_CHAT_PROMPT = "del_chp"

    NEW_COMPLETION_PROMPT = "new_cop"
    UPDATE_COMPLETION_PROMPT = "up_cop"
    DELETE_COMPLETION_PROMPT = "del_cop"

    NEW_CHAT_RESPONSE = "new_chr"
    UPDATE_CHAT_RESPONSE = "up_chr"
    DELETE_CHAT_RESPONSE = "del_chr"

    NEW_COMPLETION_RESPONSE = "new_cor"
    UPDATE_COMPLETION_RESPONSE = "up_cor"
    DELETE_COMPLETION_RESPONSE = "del_cor"


    STREAM_CHAT_RESPONSE = "stream_chr"
    STREAM_COMPLETION_RESPONSE = "stream_cop"


def update_event_queues(news: dict, project: str):
    for q in event_queues[project]:
        q.put_nowait(news)


from typing import Literal
from pydantic import Field

WEBAPP = "Webapp"
API = "API Server"


@app.get("/projects/", tags=[WEBAPP])
def read_projects() -> list[str]:
    return list_projects()


from sqlalchemy import desc, asc


@app.get(
    "/chat_prompts/",
    response_model=List[ChatPromptModel],
    response_model_exclude_unset=True,
    dependencies=[Depends(check_project_exists)],
    tags=[WEBAPP],
)
def get_chat_prompts(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    return (
        db.query(ServerChatPromptSchema).order_by(desc(ServerChatPromptSchema.created)).offset(skip).limit(limit).all()
    )


@app.get(
    "/chat_prompts/{prompt_id}",
    response_model=ChatPromptModel,
    response_model_exclude_unset=True,
    dependencies=[Depends(check_project_exists)],
    tags=[WEBAPP],
)
def get_chat_prompt(prompt_id: str, db: Session = Depends(get_session)):
    db_prompt = db.query(ServerChatPromptSchema).filter(ServerChatPromptSchema.id == prompt_id).first()

    if db_prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return db_prompt


@app.post("/chat_prompts/", response_model=ChatPromptModel, response_model_exclude_unset=True, tags=[API])
def create_chat_prompt(prompt: ChatPromptModel, project: str = "default", db: Session = Depends(get_session)):
    db_prompt = ServerChatPromptSchema(**prompt.model_dump())

    db.add(db_prompt)
    db.commit()

    model_prompt = ChatPromptModel.model_validate(db_prompt)

    update_event_queues(
        {"event": UpdateEvents.NEW_CHAT_PROMPT, "data": model_prompt.model_dump_json(exclude_unset=True)},
        project=project,
    )
    return model_prompt


@app.put(
    "/chat_prompts/{prompt_id}",
    response_model=ChatPromptModel,
    response_model_exclude_unset=True,
    dependencies=[Depends(check_project_exists)],
    tags=[API],
)
def update_chat_prompt(
    prompt_id: str, prompt: ChatPromptModel, project: str = "default", db: Session = Depends(get_session)
):
    db_prompt = db.query(ServerChatPromptSchema).filter(ServerChatPromptSchema.id == prompt_id).first()
    if db_prompt is None:
        raise HTTPException(status_code=404, detail=f"{type(prompt)} with id={id} not found")

    # if "id" in prompt:
    #     raise HTTPException(status_code=403, detail="Cannot change id")

    for key, value in prompt.model_dump().items():
        setattr(db_prompt, key, value)

    db.commit()

    model_prompt = ChatPromptModel.model_validate(db_prompt)

    update_event_queues(
        {"event": UpdateEvents.UPDATE_CHAT_PROMPT, "data": model_prompt.model_dump_json()},
        project=project,
    )

    return model_prompt


import json


@app.delete(
    "/chat_prompts/{prompt_id}",
    response_model_exclude_unset=True,
    dependencies=[Depends(check_project_exists)],
    tags=[API],
    status_code=204,
)
def delete_chat_prompt(prompt_id: str, project: str = "default", db: Session = Depends(get_session)):
    prompt = db.query(ServerChatPromptSchema).filter(ServerChatPromptSchema.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail=f"ChatPrompt with id={prompt_id} not found")
    db.delete(prompt)
    db.commit()

    # db_delete(db, DBPrompt, prompt_id)
    update_event_queues(
        {"event": UpdateEvents.DELETE_CHAT_PROMPT, "data": json.dumps({"id": prompt_id})}, project=project
    )


@app.get(
    "/chat_responses/",
    response_model=ChatResponseModel,
    response_model_exclude_unset=True,
    dependencies=[Depends(check_project_exists)],
    tags=[WEBAPP],
)
def get_chat_responses(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    return (
        db.query(ServerChatResponseSchema)
        .order_by(desc(ServerChatResponseSchema.created))
        .offset(skip)
        .limit(limit)
        .all()
    )


@app.get(
    "/chat_responses/{response_id}",
    response_model=ChatResponseModel,
    response_model_exclude_unset=True,
    dependencies=[Depends(check_project_exists)],
    tags=[WEBAPP],
)
def get_chat_response(response_id: str, db: Session = Depends(get_session)):
    db_response = db.query(ServerChatResponseSchema).filter(ServerChatResponseSchema.id == response_id).first()
    if db_response is None:
        raise HTTPException(status_code=404, detail="Response not found")
    return db_response


@app.post("/chat_responses/", response_model=ChatResponseModel, response_model_exclude_unset=True, tags=[API])
def create_response(response: ChatResponseModel, project: str = "default", db: Session = Depends(get_session)):
    existing_response = db.query(ServerChatResponseSchema).filter(ServerChatResponseSchema.id == response.id).first()
    if existing_response is not None:
        raise HTTPException(status_code=403, detail=f"Response with id={response.id} already exists")

    db_response = ServerChatResponseSchema(**response.model_dump())

    db.add(db_response)
    db.commit()

    model_response = ChatResponseModel.model_validate(db_response)

    update_event_queues(
        {"event": UpdateEvents.NEW_CHAT_RESPONSE, "data": model_response.model_dump_json()}, project=project
    )

    return model_response


@app.put(
    "/chat_responses/{response_id}",
    response_model=ChatResponse,
    response_model_exclude_unset=True,
    dependencies=[Depends(check_project_exists)],
    tags=[API],
)
def update_response(
    response_id: str, response: ChatResponseModel, project: str = "default", db: Session = Depends(get_session)
):
    db_response = db.query(ServerChatResponseSchema).filter(ServerChatResponseSchema.id == response_id).first()
    if db_response is None:
        raise HTTPException(status_code=404, detail=f"{type(response)} with id={id} not found")

    for key, value in response.model_dump().items():
        setattr(db_response, key, value)

    model_response = ChatResponseModel.model_validate(db_response)

    db.commit()
    update_event_queues(
        {"event": UpdateEvents.UPDATE_CHAT_RESPONSE, "data": model_response.model_dump_json()},
        project=project,
    )

    return db_response


@app.delete(
    "/chat_responses/{response_id}",
    response_model_exclude_unset=True,
    dependencies=[Depends(check_project_exists)],
    tags=[API],
    status_code=204,
)
def delete_response(response_id: str, project: str = "default", db: Session = Depends(get_session)):
    db_response = db.query(ServerChatResponseSchema).filter(ServerChatResponseSchema.id == response_id).first()
    if not db_response:
        raise HTTPException(status_code=404, detail=f"Response with id={response_id} not found")
    prompt_id = db.response.prompt_id
    db.delete(db_response)
    db.commit()
    update_event_queues(
        {"event": UpdateEvents.DELETE_CHAT_RESPONSE, "data": json.dumps({"id": response_id, "prompt_id": prompt_id})},
        project=project,
    )


@app.websocket("/chat_responses/{id}/update_stream")
async def record_update_ws(websocket: WebSocket, id: str, project: str = "default", db: Session = Depends(get_session)):
    await websocket.accept()
    try:
        db_response = db.query(ServerChatResponseSchema).filter(ServerChatResponseSchema.id == id).first()
        if db_response is None:
            raise HTTPException(status_code=404, detail="Response not found")

        db_response = ChatResponseModel.model_validate(db_response)

        if "content" not in db_response:
            db_response.content = ""

        stop_reson = None
        async for message in websocket.iter_text():
            ws_message = WSMessage.model_validate_json(message)
            ws_message.id = id  # We will pass the id on to the webapp via SSE, make sure it is set
            ws_message.prompt_id = db_response.prompt_id

            if ws_message.key not in db_response.__fields__:
                raise WebSocketException(
                    code=status.WS_1002_PROTOCOL_ERROR,
                    reason=f"Key {ws_message.key} not in {db_response.__class__.__name__}",
                )

            if ws_message.action == "replace":
                setattr(db_response, ws_message.key, ws_message.value)
            elif ws_message.action == "append":
                setattr(db_response, ws_message.key, getattr(db_response, ws_message.key, "") + ws_message.value)
            elif ws_message.action == "delete":
                setattr(db_response, ws_message.key, None)

            # Pass the message on to the webapp via SSE
            update_event_queues({"event": UpdateEvents.STREAM_CHAT_RESPONSE, "data": ws_message.model_dump()}, project=project)

            print(id, ws_message)

        print("Updating database", db_response)
        db.commit()

        # db_update(db, DBResponse, id, db_response)

    finally:
        print("Closing websocket")
        # await websocket.close()
        db.close()


from sse_starlette.sse import EventSourceResponse
import json

from fastapi.encoders import jsonable_encoder


@app.get("/updates/", dependencies=[Depends(check_project_exists)], tags=[WEBAPP])
def get_updates(project: str = "default") -> EventSourceResponse:
    event_queue = asyncio.Queue()
    event_queues[project].append(event_queue)

    async def event_generator():
        print("Heartbeat start")
        try:
            while True:
                news = await event_queue.get()
                payload = jsonable_encoder(dict(event=news["event"], data=news["data"]))
                print("Sending event", payload)
                yield payload
        except asyncio.CancelledError as e:
            print("Heartbeat Cancelled", e)
            event_queues[project].remove(event_queue)

    return EventSourceResponse(event_generator())
