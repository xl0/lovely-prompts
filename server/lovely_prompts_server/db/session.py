from typing import Generator

from sqlalchemy.orm import Session, sessionmaker
from starlette.requests import Request

from sqlalchemy import create_engine

from .local import Base

from fastapi import HTTPException


from contextvars import ContextVar




import appdirs
import os
from pathlib import Path



# I want to make it easy for the user to delete a project without knowing SQL or out CLI tools.
# So each project is stored in a separate sqlite file, which can be just deleted.

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
        Base.metadata.create_all(bind=engine)
    else:
        print("Database already exists")

    return engine


def check_project_exists(project="default"):
    if not project_exists(project):
        raise HTTPException(status_code=404, detail=f"Project '{project}' not found")


def list_projects():
    app_data_dir = appdirs.user_data_dir("lovely_prompts")
    dbs_dir = f"{app_data_dir}/dbs"
    os.makedirs(dbs_dir, exist_ok=True)
    project_names = os.listdir(dbs_dir)
    return [name.replace(".db", "") for name in project_names]


from contextlib import contextmanager

# This version create a new connection for every request, which is slow.
# Use for debugging if you have to.
# @contextmanager
# def get_session(request: Request, project="default"):
#     engine = project_create(project)
#     SessionLocal = sessionmaker(bind=engine)
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.commit()
#         db.close()


# Don't use as a fastapi Dependency.
# Deoendencies are cached by default, and end up being shaed between threads.
# It's way too easy to forget use_cacehe=False and have a hard to find bug.
@contextmanager
def get_session(request: Request, project="default"):
    thread_local_sm = request.app.sessionmakers.get()
    if project not in thread_local_sm:
        engine = project_create(project)
        thread_local_sm[project] = sessionmaker(bind=engine)

    db = thread_local_sm[project]()
    try:
        yield db
    finally:
        db.commit()
        db.close()

