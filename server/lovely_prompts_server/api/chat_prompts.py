from typing import List
import json

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from sqlalchemy import desc


from lovely_prompts_server.common import TAG_WEBAPP, TAG_API, UpdateEvents

from lovely_prompts_server.event_queues import update_event_queues

from lovely_prompts_server.models import ChatPromptModel, ChatPrompt, make_id
from lovely_prompts_server.db.local import ChatPromptSchema
from lovely_prompts_server.db.session import get_session, check_project_exists


router = APIRouter()


@router.get(
    "/chat_prompts/",
    response_model=List[ChatPromptModel],
    response_model_exclude_unset=True,
    dependencies=[Depends(check_project_exists)],
    tags=[TAG_WEBAPP],
)
def get_chat_prompts(request: Request, project: str = "default", skip: int = 0, limit: int = 100):
    with get_session(request=request, project=project) as db:
        chp_list =  db.query(ChatPromptSchema).order_by(desc(ChatPromptSchema.created)).offset(skip).limit(limit).all()
        chat_prompt_model_list = [ ChatPromptModel.model_validate(chp) for chp in chp_list ]
        return chat_prompt_model_list



@router.get(
    "/chat_prompts/{prompt_id}",
    response_model=ChatPromptModel,
    response_model_exclude_unset=True,
    dependencies=[Depends(check_project_exists)],
    tags=[TAG_WEBAPP],
)
def get_chat_prompt(request: Request, prompt_id: str, project: str = "project"):
    with get_session(request=request, project=project) as db:
        db_prompt = db.query(ChatPromptSchema).filter(ChatPromptSchema.id == prompt_id).first()

        if db_prompt is None:
            raise HTTPException(status_code=404, detail="Prompt not found")

        return ChatPromptModel.model_validate(db_prompt)


@router.post("/chat_prompts/", response_model=ChatPromptModel, response_model_exclude_unset=True, tags=[TAG_API])
def create_chat_prompt(request: Request, pyaload: ChatPrompt, project: str = "default"):
    with get_session(request=request, project=project) as db:
        db_prompt = ChatPromptSchema(**pyaload.model_dump(), id=make_id(ChatPrompt))
        db.add(db_prompt)
        db.commit()
        model_prompt = ChatPromptModel.model_validate(db_prompt)

        update_event_queues(
            request.app,
            {"event": UpdateEvents.NEW_CHAT_PROMPT, "data": model_prompt.model_dump_json(exclude_unset=True)},
            project=project,
        )
    return model_prompt


@router.put(
    "/chat_prompts/{prompt_id}",
    response_model=ChatPromptModel,
    response_model_exclude_unset=True,
    dependencies=[Depends(check_project_exists)],
    tags=[TAG_API],
)
def update_chat_prompt(request: Request, prompt_id: str, diff: ChatPrompt, project: str = "default"):
    with get_session(request=request, project=project) as db:
        db_prompt = db.query(ChatPromptSchema).filter(ChatPromptSchema.id == prompt_id).first()
        if db_prompt is None:
            raise HTTPException(status_code=404, detail=f"{type(diff)} with id={id} not found")

        for key, value in diff.model_dump().items():
            setattr(db_prompt, key, value)

        db.commit()
        model_prompt = ChatPromptModel.model_validate(db_prompt)

        update_event_queues(
            request.app,
            {"event": UpdateEvents.UPDATE_CHAT_PROMPT, "data": model_prompt.model_dump_json()},
            project=project,
        )

    return model_prompt


@router.delete(
    "/chat_prompts/{prompt_id}",
    response_model_exclude_unset=True,
    dependencies=[Depends(check_project_exists)],
    tags=[TAG_API],
    status_code=204,
)
def delete_chat_prompt(request: Request, prompt_id: str, project: str = "default"):
    with get_session(request=request, project=project) as db:
        prompt = db.query(ChatPromptSchema).filter(ChatPromptSchema.id == prompt_id).first()
        if not prompt:
            raise HTTPException(status_code=404, detail=f"ChatPrompt with id={prompt_id} not found")
        db.delete(prompt)

        update_event_queues(
            request.app, {"event": UpdateEvents.DELETE_CHAT_PROMPT, "data": json.dumps({"id": prompt_id})}, project=project
        )
