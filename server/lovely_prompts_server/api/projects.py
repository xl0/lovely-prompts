from fastapi import APIRouter

from lovely_prompts_server.common import TAG_WEBAPP
from lovely_prompts_server.db.session import list_projects


router = APIRouter()


@router.get("/projects/", tags=[TAG_WEBAPP])
def read_projects() -> list[str]:
    return list_projects()
