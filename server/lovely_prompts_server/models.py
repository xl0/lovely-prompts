from sqlalchemy import Column, ForeignKey, Integer, String, JSON, Float
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class DBPrompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    prompt = Column(JSON)
    comment = Column(String)
    project = Column(String)

    # Relationship to DBResponse
    responses = relationship("DBResponse", back_populates="prompt", cascade="all, delete-orphan")


class DBResponse(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False)

    # Relationship to DBPrompt
    prompt = relationship("DBPrompt", back_populates="responses")

    title = Column(String)
    response = Column(JSON)
    comment = Column(String)
    tok_in = Column(Integer)
    tok_out = Column(Integer)
    tok_max = Column(Integer)
    model = Column(String)
    temperature = Column(Float)
    provider = Column(String)
    meta = Column(JSON)
