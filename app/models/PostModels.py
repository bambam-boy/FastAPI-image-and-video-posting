import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase

from pydantic import BaseModel


class DataBaseModel(DeclarativeBase):
    pass


class PostImages(DataBaseModel):
    __tablename__ = "postimages"
    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4)
    caption = Column(Text)
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    url = Column(String, nullable=False)
    Date = Column(DateTime, default=datetime.utcnow())


class Posts(DataBaseModel):
    __tablename__ = "posts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auther = Column(String, nullable=False)
    title = Column(String, nullable=False)
    discription = Column(Text)
