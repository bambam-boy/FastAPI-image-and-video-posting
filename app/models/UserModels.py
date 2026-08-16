from app.models.ModelBase import DataBaseModel
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.orm import relationship


class User(SQLAlchemyBaseUserTableUUID, DataBaseModel):
    posts = relationship("Posts", back_populates="user")
