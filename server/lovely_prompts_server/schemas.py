from typing import List, Dict, Union
from pydantic import BaseModel, Field


class PromptBase(BaseModel):
    title: str = Field(None, example="The encounter")
    prompt: Union[List[Dict], str] = Field(None, example={"messages": [{"role": "user", "text": "Hello there"}]})
    comment: str = Field(None, example="This is a comment")
    project: str = Field(None, example="my-awesome-project1!1")

    class Config:
        orm_mode = True


class ResponseBase(BaseModel):
    prompt_id: int = Field(None, example=1)
    title: str = Field(None, example="The response")
    response: Union[Dict, str] = Field(None, example="General Kenobi!!")
    comment: str = Field(None, example="This is a response comment")
    tok_in: int = Field(None, example=10)
    tok_out: int = Field(None, example=20)
    tok_max: int = Field(None, example=8000)
    meta: Dict = Field(None)
    model: str = Field(None, example="gpt-3.5-turbo")
    temperature: float = Field(None, example=0.7)
    provider: str = Field(None, example="openai")

    class Config:
        orm_mode = True


class Response(ResponseBase):
    id: int
    # prompt: PromptBase = Field(..., alias="prompt")


class Prompt(PromptBase):
    id: int
    responses: List[ResponseBase] = Field([], alias="responses")
