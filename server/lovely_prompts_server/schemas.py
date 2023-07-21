from typing import List, Dict, Union
from pydantic import BaseModel, Field
from datetime import datetime


class _Common(BaseModel):
    title: str = Field(None, example="The encounter")
    comment: str = Field(None, example="This is a comment")

    class Config:
        orm_mode = True


class ChatMessage(BaseModel):
    role: str = Field(None, example="user")
    content: str = Field(None, example="Hello there")


class ChatPromptBase(_Common):
    messages: List[ChatMessage] = Field(None, example=[{"role": "user", "content": "Hello there"}])
    project: str = Field(None, example="my-awesome-project1!1")

    class Config:
        orm_mode = True


class ChatResponseBase(_Common):
    prompt_id: int = Field(None, example=1)
    response: ChatMessage = Field(None, example={"role": "assistant", "content": "General Kenobi!!"})
    tok_in: int = Field(None, example=10)
    tok_out: int = Field(None, example=20)
    tok_max: int = Field(None, example=8000)
    meta: Dict = Field(None)
    model: str = Field(None, example="gpt-3.5-turbo")
    temperature: float = Field(None, example=0.7)
    provider: str = Field(None, example="openai")


class SQLRowBase(BaseModel):
    id: int
    created: datetime = Field(default=None, example="2021-01-01T00:00:00.000Z")
    updated: datetime = Field(None, example="2021-01-01T00:00:00.000Z")



class ChatResponse(SQLRowBase, ChatResponseBase):
    pass
    # prompt: PromptBase = Field(..., alias="prompt")


class Prompt(SQLRowBase, ChatPromptBase):
    responses: List[ChatResponse] = Field([], alias="responses")
