from typing import List, Dict
from pydantic import BaseModel

from fastapi import Depends, FastAPI, HTTPException,WebSocket

from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine

from .models import DBPrompt, DBResponse, Base
from .schemas import ChatPrompt, ChatResponse, ChatPromptBase, ChatResponseBase, ChatMessage

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


# @app.on_event("startup")
# def create_db():
#     """Create the database if it does not exist."""
#     Base.metadata.create_all(bind=engine)

from contextvars import ContextVar

sessionmakers = ContextVar("sessionmakers", default={})


import appdirs
import os
from pathlib import Path


def project_exists(project):
    app_data_dir = appdirs.user_data_dir("lovely_prompts")
    sqlite_file = f"{app_data_dir}/dbs/{project}.db"
    return os.path.exists(sqlite_file)


def check_project_exists(project="default"):
    if not project_exists(project):
        raise HTTPException(status_code=404, detail="Project not found")


def get_session(project="default"):
    thread_local_sm = sessionmakers.get()
    if project not in thread_local_sm:
        from pathlib import Path

        app_data_dir = Path(appdirs.user_data_dir("lovely_prompts"))
        sqlite_file = app_data_dir / "dbs" / f"{project}.db"
        engine = create_engine(f"sqlite:///{sqlite_file}")
        print(engine.url)

        if not project_exists(project):
            print("Creating new database")
            os.makedirs(app_data_dir / "dbs", exist_ok=True)
            Base.metadata.create_all(bind=engine)
        else:
            print("Database already exists")

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


def db_get(db: Session, table: Base, id: int):
    return db.query(table).filter(table.id == id).first()


from typing import Optional


def db_gets(db: Session, table: Base, skip: Optional[int], limit: Optional[int]):
    query = db.query(table)
    if skip > 0:
        query = query.offset(skip)
    if limit > 0:
        query = query.limit(limit)
    return query.all()


def db_create(db: Session, table: Base, data: dict) -> Base:
    db_data = table(**data)
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data


def db_update(db: Session, table: Base, id: int, data: BaseModel) -> Base:
    db_data = db_get(db, table, id)
    if db_data is None:
        raise HTTPException(status_code=404, detail="Data not found")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(db_data, key, value)
    db.commit()


def db_delete(db: Session, table: Base, id: int):
    db_data = db_get(db, table, id)
    if db_data is None:
        raise HTTPException(status_code=404, detail="Data not found")
    db.delete(db_data)
    db.commit()


from collections import defaultdict
from functools import partial
import asyncio
import json

event_queues: Dict[str, List[asyncio.Queue]] = defaultdict(list)


def update_event_queues(news: dict, project: str):
    for q in event_queues[project]:
        q.put_nowait(news)


webapp_tags = ["Webapp"]
apiserver_tags = ["API Server"]


@app.get("/projects/", tags=webapp_tags)
def read_projects() -> list[str]:
    return list_projects()


@app.get("/prompts/", response_model=List[ChatPrompt], dependencies=[Depends(check_project_exists)], tags=webapp_tags)
def read_prompts(skip: int = 0, limit: int = 0, db: Session = Depends(get_session)):
    prompts = db_gets(db, DBPrompt, skip=skip, limit=limit)
    return prompts


@app.get(
    "/prompts/{prompt_id}", response_model=ChatPrompt, dependencies=[Depends(check_project_exists)], tags=webapp_tags
)
def read_prompt(prompt_id: int, db: Session = Depends(get_session)):
    db_prompt = db_get(db, DBPrompt, prompt_id)
    if db_prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return db_prompt


from fastapi.encoders import jsonable_encoder

@app.post("/prompts/", response_model=ChatPrompt, tags=apiserver_tags)
def create_prompt(prompt: ChatPromptBase, project: str = "default", db: Session = Depends(get_session)):
    res = db_create(db, DBPrompt, prompt.dict())
    update_event_queues({"event": "create_prompt", "data": ChatPrompt.from_orm(res).json()}, project=project)
    return res
@app.put(
    "/prompts/{prompt_id}", response_model=ChatPrompt, dependencies=[Depends(check_project_exists)], tags=apiserver_tags
)
def update_prompt(prompt_id: int, prompt: ChatPromptBase, project: str = "default", db: Session = Depends(get_session)):
    db_update(db, DBPrompt, prompt_id, prompt)
    db_prompt = db_get(db, DBPrompt, prompt_id)
    update_event_queues({"event": "update_prompt", "data": ChatPrompt.from_orm(db_prompt).json()}, project=project)

    return db_prompt


@app.delete("/prompts/{prompt_id}", dependencies=[Depends(check_project_exists)], tags=apiserver_tags)
def delete_prompt(prompt_id: int, project: str = "default", db: Session = Depends(get_session)):
    db_delete(db, DBPrompt, prompt_id)
    update_event_queues({"event": "delete_prompt", "data": json.dumps({"id": prompt_id})}, project=project)


@app.get(
    "/responses/", response_model=List[ChatResponse], dependencies=[Depends(check_project_exists)], tags=webapp_tags
)
def read_responses(skip: int = 0, limit: int = 0, db: Session = Depends(get_session)):
    responses = db_gets(db, DBResponse, skip=skip, limit=limit)
    return responses


@app.get(
    "/responses/{response_id}",
    response_model=ChatResponse,
    dependencies=[Depends(check_project_exists)],
    tags=webapp_tags,
)
def read_response(response_id: int, db: Session = Depends(get_session)):
    db_response = db_get(db, DBResponse, response_id)
    if db_response is None:
        raise HTTPException(status_code=404, detail="Response not found")
    return db_response


@app.post("/responses/", response_model=ChatResponse, tags=apiserver_tags)
def create_response(response: ChatResponseBase, project: str = "default", db: Session = Depends(get_session)):
    res = db_create(db, DBResponse, response.dict())
    update_event_queues({"event": "create_response", "data": ChatResponse.from_orm(res).json()}, project=project)
    return res

@app.put(
    "/responses/{response_id}",
    response_model=ChatResponse,
    dependencies=[Depends(check_project_exists)],
    tags=apiserver_tags,
)
def update_response(response_id: int, response: ChatResponseBase, project: str = "default", db: Session = Depends(get_session)):
    db_update(db, DBResponse, response_id, response)
    db_response = db_get(db, DBResponse, response_id)
    update_event_queues({"event": "update_response", "data": ChatResponse.from_orm(db_response).json()}, project=project)

    return db_response

@app.delete("/responses/{response_id}", dependencies=[Depends(check_project_exists)], tags=apiserver_tags)
def delete_response(response_id: int, project: str = "default", db: Session = Depends(get_session)):
    db_response = db_get(db, DBResponse, response_id)
    prompt_id = db_response.prompt_id
    db_delete(db, DBResponse, response_id)
    update_event_queues({"event": "delete_response", "data": json.dumps({"id": response_id, "prompt_id": prompt_id})}, project=project)

@app.websocket("/responses/{id}/stream_in")
async def stream_in(websocket: WebSocket, id:str, project: str = "default", db: Session = Depends(get_session)):
    await websocket.accept()
    try:
        db_response = db_get(db, DBResponse, id)
        if db_response is None:
            raise HTTPException(status_code=404, detail="Response not found")

        db_response = ChatResponse.from_orm(db_response)

        content = db_response.response.content
        async for message in websocket.iter_text():
            print(id, message)
            content += message

            update_event_queues({"event": "stream_in", "data": json.dumps({"id": id, "prompt_id": db_response.prompt_id, "message": message})}, project=project)
        db_update(db, DBResponse, id, ChatResponseBase(response=ChatMessage(content=content)))

    finally:
        print("Closing websocket")
        await websocket.close()
        db.close()


from sse_starlette.sse import EventSourceResponse
import json

@app.get("/updates/", dependencies=[Depends(check_project_exists)], tags=webapp_tags)
def get_updates(project: str = "default") -> EventSourceResponse:
    event_queue = asyncio.Queue()
    event_queues[project].append(event_queue)

    async def event_generator():
        print("Heartbeat start")
        try:
            while True:
                news = await event_queue.get()
                print("Sending event", news)
                yield dict(event=news["event"], data=news["data"])
        except asyncio.CancelledError as e:
            print("Heartbeat Cancelled", e)
            event_queues[project].remove(event_queue)

    return EventSourceResponse(event_generator())


# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse


# app.mount("/", StaticFiles(directory="../webapp/build/", html=True), name="static")

# @app.get("/{path_name}")
# async def index(path_name: str):
#     print(path_name)
#     return FileResponse("../webapp/build/index.html")


import uvicorn

if __name__ == "__main__":
    uvicorn.run(app)
