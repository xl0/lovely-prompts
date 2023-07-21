from typing import List

from fastapi import Depends, FastAPI, HTTPException

from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine

from .models import DBPrompt, DBResponse, Base
from .schemas import ChatPrompt, ChatResponse, ChatPromptBase, ChatResponseBase

engine = create_engine("sqlite:///./sql_app.db")
SessionLocal = sessionmaker(autoflush=True, bind=engine)

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


@app.on_event("startup")
def create_db():
    """Create the database if it does not exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


def db_update(db: Session, table: Base, id: int, data: dict) -> Base:
    db_data = db_get(db, table, id)
    if db_data is None:
        raise HTTPException(status_code=404, detail="Data not found")
    for key, value in data.items():
        setattr(db_data, key, value)
    db.commit()


def db_delete(db: Session, table: Base, id: int):
    db_data = db_get(db, table, id)
    if db_data is None:
        raise HTTPException(status_code=404, detail="Data not found")
    db.delete(db_data)
    db.commit()


from collections import OrderedDict


@app.get("/prompts/", response_model=List[ChatPrompt])
def read_prompts(skip: int = 0, limit: int = 0, db: Session = Depends(get_db)):
    prompts = db_gets(db, DBPrompt, skip=skip, limit=limit)
    return prompts


@app.get("/prompts/{prompt_id}", response_model=ChatPrompt)
def read_prompt(prompt_id: int, db: Session = Depends(get_db)):
    db_prompt = db_get(db, DBPrompt, prompt_id)
    if db_prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return db_prompt


@app.post("/prompts/", response_model=ChatPrompt)
def create_prompt(prompt: ChatPromptBase, db: Session = Depends(get_db)):
    return db_create(db, DBPrompt, prompt.dict())


@app.put("/prompts/{prompt_id}", response_model=ChatPrompt)
def update_prompt(prompt_id: int, prompt: ChatPromptBase, db: Session = Depends(get_db)):
    db_update(db, DBPrompt, prompt_id, prompt.dict())
    db_prompt = db_get(db, DBPrompt, prompt_id)
    return db_prompt


@app.delete("/prompts/{prompt_id}")
def delete_prompt(prompt_id: int, db: Session = Depends(get_db)):
    db_delete(db, DBPrompt, prompt_id)


@app.get("/responses/", response_model=List[ChatResponse])
def read_responses(skip: int = 0, limit: int = 0, db: Session = Depends(get_db)):
    responses = db_gets(db, DBResponse, skip=skip, limit=limit)
    return responses


@app.get("/responses/{response_id}", response_model=ChatResponse)
def read_response(response_id: int, db: Session = Depends(get_db)):
    db_response = db_get(db, DBResponse, response_id)
    if db_response is None:
        raise HTTPException(status_code=404, detail="Response not found")
    return db_response


@app.get("/responses/{response_id}", response_model=ChatResponse)
def read_response(response_id: int, db: Session = Depends(get_db)):
    db_response = db_get(db, DBResponse, response_id)
    if db_response is None:
        raise HTTPException(status_code=404, detail="Response not found")
    return db_response


@app.post("/responses/", response_model=ChatResponse)
def create_response(response: ChatResponseBase, db: Session = Depends(get_db)):
    return db_create(db, DBResponse, response.dict())


@app.put("/responses/{response_id}", response_model=ChatResponse)
def update_response(response_id: int, response: ChatResponseBase, db: Session = Depends(get_db)):
    db_update(db, DBResponse, response_id, response.dict())
    db_response = db_get(db, DBResponse, response_id)
    return db_response


@app.delete("/responses/{response_id}")
def delete_response(response_id: int, db: Session = Depends(get_db)):
    db_delete(db, DBResponse, response_id)


from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


# @app.api_route("/{path_name:path}", methods=["GET"])
# async def catch_all(request: Request, path_name: str):
#     return {"request_method": request.method, "path_name": path_name}

app.mount("/", StaticFiles(directory="../webapp/build/", html=True), name="static")


@app.get("/{path_name}")
async def index(path_name: str):
    print(path_name)
    return FileResponse("../webapp/build/index.html")


import uvicorn

if __name__ == "__main__":
    uvicorn.run(app)
