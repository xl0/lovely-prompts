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


# class PromptTemplateBody(BaseModelNoUset):
#     filename: str = Field(None, example="template.jn2")
#     type: str = Field(None, example="jinja2")


# class PromptTemplateData(BaseModelNoUset):
#     data: Dict[str, Any] = Field(None, example={"name": "John"})



class ChatMessage(RowCommon):
    role: str = Field(None, example="user")
    content: str = Field(None, example="Hello there")
    # template_id: Optional[str] = Field(None, example="tem_1234")





class ResponseBase(RowCommon):
    prompt_id: str = Field(None, example="chp_234243242")

    content: Optional[str] = Field(None, example="Flat, of course!")
    stop_reason: Optional[str] = Field(None, example="length")

    tok_in: Optional[int] = Field(None, example=10)
    tok_out: Optional[int] = Field(None, example=20)
    tok_max: Optional[int] = Field(None, example=8000)
    meta: Optional[Dict] = Field(None)
    model: Optional[str] = Field(None, example="gpt-3.5-turbo")
    temperature: Optional[float] = Field(None, example=0.7)
    provider: Optional[str] = Field(None, example="openai")



class ChatResponse(ResponseBase):
    role: Optional[str] = Field(None, example="assistant", desc="'assistant' or similar")
    # run_id: Optional[str] = Field(None, example="run_Cf5Gjbv9TCUSIexr")

class ChatPrompt(RowCommon):
    prompt: Optional[List[ChatMessage]] = Field(
        None, example=[{"role": "user", "content": "What is the true shape of the Earth???"}]
    )
    responses: List[ChatResponse] = Field([], alias="responses")
    # run_id: Optional[str] = Field(None, example="run_Cf5Gjbv9TCUSIexr")


class CompletionResponse(ResponseBase):
    # run_id: Optional[str] = Field(None, example="run_Cf5Gjbv9TCUSIexr")
    pass

class CompletionPrompt(RowCommon):
    prompt: str = Field("", example="Bush did")
    responses: List[CompletionResponse] = Field([], alias="responses")
    # run_id: Optional[str] = Field(None, example="run_Cf5Gjbv9TCUSIexr")


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

# Don't forget to update the webapp if you change this
class WSMessage(BaseModelNoUset):
    id: Optional[str] = None
    prompt_id: Optional[str] = None
    action: Literal["replace", "append", "delete"]
    key: str
    value: Union[str, int, float, bool]



from functools import partial
import string
import nanoid


generate_nonoid = partial(nanoid.generate, size=16)

def make_id(entry_class=None):
    """Generate a unique ID for a DB entry. Also used to generate the name of the DB file."""

    prefixes = {
        ChatPrompt: "chp_",
        CompletionPrompt: "cop_",
        ChatResponse: "chr_",
        CompletionResponse: "cor_",
    }

    alphabet = string.digits + string.ascii_lowercase + string.ascii_uppercase

    return (prefixes[entry_class] if entry_class else "") + generate_nonoid(alphabet=alphabet)



