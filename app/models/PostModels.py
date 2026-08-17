import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.ModelBase import DataBaseModel


class Posts(DataBaseModel):
    __tablename__ = "posts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    auther = Column(String, nullable=False)
    title = Column(String, nullable=False)
    discription = Column(Text)
    user = relationship("User", back_populates="posts")
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    url = Column(String, nullable=False)
    Date = Column(DateTime, default=datetime.utcnow())
