# from typing import List

# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from sqlalchemy import desc

# from fastapi import APIRouter

# from lovely_prompts_server.common import TAG_WEBAPP
# from lovely_prompts_server.models import RunModel
# from lovely_prompts_server.db.local import RunSchema
# from lovely_prompts_server.db.session import get_session, check_project_exists

# router = APIRouter()


# @router.get(
#     "/runs/",
#     response_model=List[RunModel],
#     response_model_exclude_unset=True,
#     dependencies=[Depends(check_project_exists)],
#     tags=[TAG_WEBAPP],
# )
# def get_runs(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
#     return db.query(RunSchema).order_by(desc(RunSchema.created)).offset(skip).limit(limit).all()


# @router.get(
#     "/runs/{run_id}",
#     response_model=RunModel,
#     response_model_exclude_unset=True,
#     dependencies=[Depends(check_project_exists)],
#     tags=[TAG_WEBAPP],
# )
# def get_run(run_id: str, db: Session = Depends(get_session)):
#     db_run = db.query(RunSchema).filter(RunSchema.id == run_id).first()

#     if db_run is None:
#         raise HTTPException(status_code=404, detail="Run not found")
#     return db_run
