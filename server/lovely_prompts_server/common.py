from enum import Enum

TAG_WEBAPP = "Webapp"
TAG_API = "API Server"


# Don't forget to sync with the webapp
class UpdateEvents(Enum):
    NEW_CHAT_PROMPT = "new_chp"
    UPDATE_CHAT_PROMPT = "up_chp"
    DELETE_CHAT_PROMPT = "del_chp"

    NEW_COMPLETION_PROMPT = "new_cop"
    UPDATE_COMPLETION_PROMPT = "up_cop"
    DELETE_COMPLETION_PROMPT = "del_cop"

    NEW_CHAT_RESPONSE = "new_chr"
    UPDATE_CHAT_RESPONSE = "up_chr"
    DELETE_CHAT_RESPONSE = "del_chr"

    NEW_COMPLETION_RESPONSE = "new_cor"
    UPDATE_COMPLETION_RESPONSE = "up_cor"
    DELETE_COMPLETION_RESPONSE = "del_cor"

    STREAM_CHAT_RESPONSE = "stream_chr"
    STREAM_COMPLETION_RESPONSE = "stream_cop"
