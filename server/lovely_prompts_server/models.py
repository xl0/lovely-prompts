from typing import Any, List, Dict, Union, Optional, Literal
from typing_extensions import Literal
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

from typing import Type


class BaseModelNoUset(BaseModel):
    # Call the parent class's method, but exclude_unset and exclude_none defaults to True
    def model_dump_json(
        self,
        *,
        indent: int | None = None,
        include=None,
        exclude=None,
        by_alias: bool = False,
        exclude_unset: bool = True,
        exclude_defaults: bool = False,
        exclude_none: bool = True,
        round_trip: bool = False,
        warnings: bool = True
    ) -> str:
        return super().model_dump_json(
            indent=indent,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
        )

    # Call the parent class's method, but exclude_unset and exclude_none defaults to True
    def model_dump(
        self,
        *,
        mode: str = "python",
        include=None,
        exclude=None,
        by_alias: bool = False,
        exclude_unset: bool = True,
        exclude_defaults: bool = False,
        exclude_none: bool = True,
        round_trip: bool = False,
        warnings: bool = True
    ) -> dict[str, Any]:
        return super().model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
        )



# Common fields for all SQL tables
class SqlMeta(BaseModelNoUset):
    id: Optional[str] = Field(None, example="chp_Cf5Gjbv9TCUSIexr")
    created: datetime = Field(default=None, example="2021-01-01T00:00:00.000Z")
    updated: datetime = Field(default=None, example="2021-01-01T00:00:00.000Z")

    synced: Optional[bool] = Field(default=False, description="Only used for the local caching DB")

class RowCommon(BaseModelNoUset):

    title: Optional[str] = Field(None, example="The encounter")
    comment: Optional[str] = Field(None, example="This is a comment")

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class ServerRowCommon(RowCommon):
    # At the moment the server version of the database does not have any extra fields,
    # but I expect them in the future.
    pass


class ChatMessage(RowCommon):
    role: str = Field(None, example="user")
    content: str = Field(None, example="Hello there")


class ResponseBase(RowCommon):
    prompt_id: str = Field(None, example=1)

    content: Optional[str] = Field(None, example="Flat, of course!")
    stop_reason: Optional[str] = Field(None, example="length")

    tok_in: Optional[int] = Field(None, example=10)
    tok_out: Optional[int] = Field(None, example=20)
    tok_max: Optional[int] = Field(None, example=8000)
    meta: Optional[Dict] = Field(None)
    model: Optional[str] = Field(None, example="gpt-3.5-turbo")
    temperature: Optional[float] = Field(None, example=0.7)
    provider: Optional[str] = Field(None, example="openai")


class CompletionResponse(ResponseBase):
    pass


class ChatResponse(ResponseBase):
    role: Optional[str] = Field(None, example="assistant", desc="'assistant' or similar")


class ChatPrompt(RowCommon):
    prompt: Optional[List[ChatMessage]] = Field(
        None, example=[{"role": "user", "content": "What is the true shape of the Earth???"}]
    )
    responses: List[ChatResponse] = Field([], alias="responses")


class CompletionPrompt(RowCommon):
    prompt: str = Field("", example="Bush did")
    responses: List[CompletionResponse] = Field([], alias="responses")


# A record with the common SQL fields. This is used to pass the data to/from the server endpoints.
class ChatPromptModel(ChatPrompt, SqlMeta):
    pass


class CompletionPromptModel(CompletionPrompt, SqlMeta):
    pass


class ChatResponseModel(ChatResponse, SqlMeta):
    pass


class CompletionResponseModel(CompletionResponse, SqlMeta):
    pass


# Then it gets synced to the server, which migiht add extra fields to the records.
class ServerChatPromptModel(ChatPrompt, ServerRowCommon):
    pass


class ServerCompletionPromptModel(CompletionPrompt, ServerRowCommon):
    pass


class ServerChatResponseModel(ChatResponse, ServerRowCommon):
    pass


class ServerCompletionResponseModel(CompletionResponse, ServerRowCommon):
    pass


class WSMessage(BaseModelNoUset):
    id: Optional[str]
    prompt_id: Optional[str]
    action: Literal["replace", "append", "delete"]
    key: str
    value: str


