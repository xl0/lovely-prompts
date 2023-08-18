
from sqlalchemy import Column, Boolean, String, ForeignKey, JSON
from sqlalchemy.orm import relationship, declarative_base
from .common import EntryMeta, ResponseMeta

LocalBase = declarative_base()

class LocalChatPromptSchema(LocalBase, EntryMeta):
    __tablename__ = "local_chat_prompts"

    prompt = Column(JSON)
    responses = relationship("LocalChatResponseSchema", back_populates="prompt", cascade="all, delete-orphan")


class LocalCompletionPromptSchema(LocalBase, EntryMeta):
    __tablename__ = "local_completion_prompts"

    prompt = Column(String)
    responses = relationship("LocalCompletionResponseSchema", back_populates="prompt", cascade="all, delete-orphan")


class LocalCompletionResponseSchema(LocalBase, EntryMeta, ResponseMeta):
    __tablename__ = "local_completion_responses"

    prompt_id = Column(String, ForeignKey("local_completion_prompts.id"), nullable=False)
    prompt = relationship("LocalCompletionPromptSchema", back_populates="responses")


class LocalChatResponseSchema(LocalBase, EntryMeta, ResponseMeta):
    __tablename__ = "local_chat_responses"

    prompt_id = Column(String, ForeignKey("local_chat_prompts.id"), nullable=False)
    prompt = relationship("LocalChatPromptSchema", back_populates="responses")

    role = Column(String)  # "assistant" or similar