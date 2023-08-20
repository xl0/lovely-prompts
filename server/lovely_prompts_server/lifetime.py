from typing import Awaitable, Callable, Dict, List
from fastapi import FastAPI
from contextvars import ContextVar

from asyncio import Queue
from collections import defaultdict

from lovely_prompts_server.db.session import project_create



def register_startup_event(
    app: FastAPI,
) -> Callable[[], Awaitable[None]]:  # pragma: no cover
    """
    Actions to run on application startup.

    This function uses fastAPI app to store data
    in the state, such as db_engine.

    :param app: the fastAPI application.
    :return: function that actually performs actions.
    """

    # @app.on_event("startup")
    # async def _startup() -> None:  # noqa: WPS430

    app.sessionmakers = ContextVar("sessionmakers", default={})
    app.event_queues: Dict[str, List[Queue]] = defaultdict(list)

    project_create("default")
    print("Startup done")

    # return _startup
