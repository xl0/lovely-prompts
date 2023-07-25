from typing import List, Dict, Union, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class _Common(BaseModel):
    title: str = Field(None, example="The encounter")
    comment: str = Field(None, example="This is a comment")

    class Config:
        orm_mode = True


class ChatMessage(_Common):
    role: str = Field(None, example="user")
    content: str = Field(None, example="Hello there")


class LLMPromptBase(_Common):
    chat_messages: Optional[List[ChatMessage]] = Field(
        None, example=[{"role": "user", "content": "The true shape of the earth is"}]
    )
    completion_prompt: Optional[str] = Field(None, example="")

    class Config:
        orm_mode = True


class LLMResponseBase(_Common):
    prompt_id: int = Field(None, example=1)

    role: str = Field(
        None, example="assistant", desc="'assistant' or similar in chat. None if a completion-type response."
    )
    content: str = Field(None, example="flat, of course!")
    stop_reason: str = Field(None, example="length")

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


class LLMResponse(SQLRowBase, LLMResponseBase):
    pass
    # prompt: PromptBase = Field(..., alias="prompt")


class LLMPrompt(SQLRowBase, LLMPromptBase):
    responses: List[LLMResponse] = Field([], alias="responses")


class WSMessage(BaseModel):
    id: Optional[int]
    prompt_id: Optional[int]
    action: Literal["replace", "append", "delete"]
    key: str
    value: str
