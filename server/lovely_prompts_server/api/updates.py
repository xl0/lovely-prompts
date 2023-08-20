
from sse_starlette.sse import EventSourceResponse
import json

from fastapi.encoders import jsonable_encoder
import fastapi
from fastapi import Depends, Request

import asyncio

from lovely_prompts_server.common import TAG_WEBAPP
from lovely_prompts_server.db.session import check_project_exists

from lovely_prompts_server.event_queues import append_event_queue, remove_event_queue

router = fastapi.APIRouter()

@router.get("/updates/", dependencies=[Depends(check_project_exists)], tags=[TAG_WEBAPP])
async def get_updates(request: Request, project: str = "default") -> EventSourceResponse:
    # event_queue = asyncio.Queue()
    # event_queues[project].append(event_queue)

    event_queue = append_event_queue(request.app, project=project)

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
        finally:
            print("Heartbeat finally")
            remove_event_queue(request.app, event_queue, project=project)


    return EventSourceResponse(event_generator())
