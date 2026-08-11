from pydantic import BaseModel


class PostModel(BaseModel):
    auther: str
    title: str
    discription: str
