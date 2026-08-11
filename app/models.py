import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


class DataBaseModel(DeclarativeBase):
    __tablename__ = "posts"
    id = Column(UUID(as_uuid=True), primary_key=True,
                dialect_kwargs=uuid.uuid4)
    caption = Column(Text)
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    Date = Column(DateTime, default=datetime.utcnow())
