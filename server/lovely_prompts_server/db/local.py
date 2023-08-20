from sqlalchemy import Column, Integer, JSON, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from lovely_prompts_server.db.common import EntryMeta, ResponseMeta


Base = declarative_base()


# class RunSchema(Base, EntryMeta):
#     __tablename__ = "runs"

#     chat_prompts = relationship("ChatPromptSchema", back_populates="run", cascade="all, delete-orphan")
#     completion_prompts = relationship("CompletionPromptSchema", back_populates="run", cascade="all, delete-orphan")

#     chat_responses = relationship("ChatResponseSchema", back_populates="run", cascade="all, delete-orphan")
#     completion_responses = relationship("CompletionResponseSchema", back_populates="run", cascade="all, delete-orphan")


class ChatPromptSchema(Base, EntryMeta):
    __tablename__ = "chat_prompts"

    # run_id = Column(String, ForeignKey("runs.id"), nullable=True)
    # run = relationship("RunSchema", back_populates="chat_prompts")

    prompt = Column(JSON)
    responses = relationship("ChatResponseSchema", back_populates="prompt", cascade="all, delete-orphan")


class ChatResponseSchema(Base, EntryMeta, ResponseMeta):
    __tablename__ = "chat_responses"

    # run_id = Column(String, ForeignKey("runs.id"), nullable=True)
    # run = relationship("RunSchema", back_populates="chat_responses")

    prompt_id = Column(String, ForeignKey("chat_prompts.id"), nullable=False)
    prompt = relationship("ChatPromptSchema", back_populates="responses")

    role = Column(String)  # "assistant" or similar


class CompletionPromptSchema(Base, EntryMeta):
    __tablename__ = "completion_prompts"

    # run_id = Column(String, ForeignKey("runs.id"), nullable=True)
    # run = relationship("RunSchema", back_populates="completion_prompts")

    prompt = Column(String)

    responses = relationship("CompletionResponseSchema", back_populates="prompt", cascade="all, delete-orphan")


class CompletionResponseSchema(Base, EntryMeta, ResponseMeta):
    __tablename__ = "completion_responses"

    # run_id = Column(String, ForeignKey("runs.id"), nullable=True)
    # run: RunSchema = relationship("RunSchema", back_populates="completion_responses")

    prompt_id = Column(String, ForeignKey("completion_prompts.id"), nullable=False)
    prompt = relationship("CompletionPromptSchema", back_populates="responses")


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
