from sqlalchemy import Column, Integer, JSON, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from .common import EntryMeta, ResponseMeta


ServerBase = declarative_base()


class ServerRowCommon(EntryMeta):
    """A DB entry is an entry that's been synced to the server.
    Right now it's the same as EntryMeta, but in the future it
    will likely acquire some server-specific fields.
    """


class ServerChatPromptSchema(ServerBase, ServerRowCommon):
    __tablename__ = "chat_prompts"

    prompt = Column(JSON)
    responses = relationship("ServerChatResponseSchema", back_populates="prompt", cascade="all, delete-orphan")


class ServerCompletionPromptSchema(ServerBase, ServerRowCommon):
    __tablename__ = "completion_prompts"

    prompt = Column(String)
    responses = relationship("ServerCompletionResponseSchema", back_populates="prompt", cascade="all, delete-orphan")


class ServerCompletionResponseSchema(ServerBase, ServerRowCommon, ResponseMeta):
    __tablename__ = "completion_responses"

    prompt_id = Column(String, ForeignKey("completion_prompts.id"), nullable=False)
    prompt = relationship("ServerCompletionPromptSchema", back_populates="responses")


class ServerChatResponseSchema(ServerBase, ServerRowCommon, ResponseMeta):
    __tablename__ = "chat_responses"

    prompt_id = Column(String, ForeignKey("chat_prompts.id"), nullable=False)
    prompt = relationship("ServerChatPromptSchema", back_populates="responses")

    role = Column(String)  # "assistant" or similar


# class DBTemplate(Base, DBEntry):
#     __tablename__ = "templates"

#     filename = Column(String)
#     type = Column(String)
#     body = Column(String)
#     instances = relationship("DBTEmplateData", back_populates="template", cascade="all, delete-orphan")


# class DBTEmplateInstance(Base, DBEntry):
#     __tablename__ = "template_instances"

#     template_id = Column(String, ForeignKey("templates.id"), nullable=False)
#     template = relationship("DBTemplate", back_populates="template_data")
#     data = Column(JSON)

#     prompts = relationship("DBPrompt", back_populates="template_data", cascade="all, delete-orphan")
