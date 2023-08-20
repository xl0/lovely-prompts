from typing import List
import json

import fastapi
from fastapi import Depends, HTTPException, Request

from sqlalchemy.orm import Session

from sqlalchemy import desc


from lovely_prompts_server.common import TAG_WEBAPP, TAG_API, UpdateEvents

from lovely_prompts_server.event_queues import update_event_queues

from lovely_prompts_server.models import ChatResponseModel, ChatResponse, WSMessage, make_id
from lovely_prompts_server.db.local import ChatResponseSchema
from lovely_prompts_server.db.session import get_session, check_project_exists

router = fastapi.APIRouter()


@router.get(
    "/chat_responses/",
    response_model=ChatResponseModel,
    response_model_exclude_unset=True,
    dependencies=[Depends(check_project_exists)],
    tags=[TAG_WEBAPP],
)
def get_chat_responses(request: Request, project: str = "defautl", skip: int = 0, limit: int = 100):
    with get_session(request=request, project=project) as db:
        db_responses = (
            db.query(ChatResponseSchema).order_by(desc(ChatResponseSchema.created)).offset(skip).limit(limit).all()
        )
        return [ChatResponseModel.model_validate(chr) for chr in db_responses]


@router.get(
    "/chat_responses/{response_id}",
    response_model=ChatResponseModel,
    response_model_exclude_unset=True,
    dependencies=[Depends(check_project_exists)],
    tags=[TAG_WEBAPP],
)
def get_chat_response(response_id: str, request: Request, project: str = "default"):
    with get_session(request=request, project=project) as db:
        db_response = db.query(ChatResponseSchema).filter(ChatResponseSchema.id == response_id).first()
        if db_response is None:
            raise HTTPException(status_code=404, detail="Response not found")
        return ChatResponseModel.model_validate(db_response)


@router.post("/chat_responses/", response_model=ChatResponseModel, response_model_exclude_unset=True, tags=[TAG_API])
def create_response(request: Request, payload: ChatResponse, project: str = "default"):
    with get_session(request=request, project=project) as db:
        db_response = ChatResponseSchema(**payload.model_dump(), id=make_id(ChatResponse))

        db.add(db_response)
        db.commit()

        model_response = ChatResponseModel.model_validate(db_response)

        update_event_queues(
            request.app,
            {"event": UpdateEvents.NEW_CHAT_RESPONSE, "data": model_response.model_dump_json()}, project=project
        )

        return model_response


@router.put(
    "/chat_responses/{response_id}",
    response_model=ChatResponse,
    response_model_exclude_unset=True,
    dependencies=[Depends(check_project_exists)],
    tags=[TAG_API],
)
def update_response(
    request: Request,
    response_id: str,
    diff: ChatResponse,
    project: str = "default",
):

    with get_session(request=request, project=project) as db:
        db_response = db.query(ChatResponseSchema).filter(ChatResponseSchema.id == response_id).first()
        if db_response is None:
            raise HTTPException(status_code=404, detail=f"{type(diff)} with id={id} not found")

        for key, value in diff.model_dump().items():
            setattr(db_response, key, value)

        db.commit()
        model_response = ChatResponseModel.model_validate(db_response)

        update_event_queues(
            request.app,
            {"event": UpdateEvents.UPDATE_CHAT_RESPONSE, "data": model_response.model_dump_json()},
            project=project,
        )

        return db_response


@router.delete(
    "/chat_responses/{response_id}",
    response_model_exclude_unset=True,
    dependencies=[Depends(check_project_exists)],
    tags=[TAG_API],
    status_code=204,
)
def delete_response(request: Request, response_id: str, project: str = "default"):
    with get_session(request=request, project=project) as db:
        db_response = db.query(ChatResponseSchema).filter(ChatResponseSchema.id == response_id).first()
        if not db_response:
            raise HTTPException(status_code=404, detail=f"Response with id={response_id} not found")
        prompt_id = db.response.prompt_id
        db.delete(db_response)
        update_event_queues(
            request.app,
            {"event": UpdateEvents.DELETE_CHAT_RESPONSE, "data": json.dumps({"id": response_id, "prompt_id": prompt_id})},
            project=project,
        )


@router.websocket("/chat_responses/{id}/update_stream/")
async def record_update_ws(
    websocket: fastapi.WebSocket, id: str, project: str = "default"
):
    await websocket.accept()
    with get_session(request=websocket, project=project) as db:
        try:
            db_response = db.query(ChatResponseSchema).filter(ChatResponseSchema.id == id).first()
            if db_response is None:
                raise HTTPException(status_code=404, detail="Response not found")

            # db_response = ChatResponseModel.model_validate(db_response)

            if db_response.content is None:
                db_response.content = ""

            stop_reson = None
            async for message in websocket.iter_text():
                ws_message = WSMessage.model_validate_json(message)
                ws_message.id = id  # We will pass the id on to the webapp via SSE, make sure it is set
                ws_message.prompt_id = db_response.prompt_id

                if ws_message.key not in db_response.__table__.columns.keys():
                    raise fastapi.WebSocketException(
                        code=fastapi.status.WS_1002_PROTOCOL_ERROR,
                        reason=f"Key {ws_message.key} not in {db_response.__class__.__name__}",
                    )

                if ws_message.action == "replace":
                    setattr(db_response, ws_message.key, ws_message.value)
                elif ws_message.action == "append":
                    setattr(db_response, ws_message.key, getattr(db_response, ws_message.key, "") + ws_message.value)
                elif ws_message.action == "delete":
                    setattr(db_response, ws_message.key, None)

                # Pass the message on to the webapp via SSE
                update_event_queues(
                    websocket.app,
                    {"event": UpdateEvents.STREAM_CHAT_RESPONSE, "data": ws_message.model_dump_json()}, project=project
                )

                print(id, ws_message)

            print("Updating database", db_response)
            # db.commit()

            # db_update(db, DBResponse, id, db_response)

        finally:
            print("Closing websocket")
            # await websocket.close()

