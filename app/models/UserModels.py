from app.models.ModelBase import DataBaseModel
from sqlalchemy import String, Column
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy.orm import relationship


class User(SQLAlchemyBaseUserTableUUID, DataBaseModel):
    posts = relationship("Posts", back_populates="user")
    username = Column(String, nullable=False)
