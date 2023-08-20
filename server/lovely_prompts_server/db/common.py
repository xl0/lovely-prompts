from sqlalchemy import Column, ForeignKey, Integer, String, JSON, Float, DateTime, func, Boolean
from sqlalchemy.orm import declarative_base, relationship

# Base = declarative_base()


class EntryMeta:
    """Common fields for all entries. Entries are things like ChatPrompt, CompletionPrompt, etc."""

    id = Column(String, index=True, primary_key=True, unique=True)
    title = Column(String)
    comment = Column(String)

    # Only used for the local caching DB, but I want to avoid excessive classes.
    synced = Column(Boolean, default=False)

    created = Column(DateTime(timezone=True), default=func.now())
    updated = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())


class ResponseMeta:
    """Common fields for ChatResponse and CompletionResponse."""

    content = Column(String)
    stop_reason = Column(String)

    tok_in = Column(Integer)
    tok_out = Column(Integer)
    tok_max = Column(Integer)
    model = Column(String)
    temperature = Column(Float)
    provider = Column(String)
    meta = Column(JSON)
