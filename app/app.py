from fastapi import FastAPI, HTTPException, Form, File, UploadFile, Depends
from app.models import PostModel
from app.core.db import creat_db_and_table, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await creat_db_and_table()
    yield

app = FastAPI(lifespan=lifespan)

text_posts = {
    "1": {
        "auther": "sara",
        "title": "how to learn python fast",
        "discription": "tips and tricks for beginners"
    },
    "2": {
        "auther": "reza",
        "title": "best movies of 2025",
        "discription": "top 10 must-watch films"
    },
    "3": {
        "auther": "mina",
        "title": "healthy breakfast ideas",
        "discription": "quick and delicious recipes"
    },
    "4": {
        "auther": "ali reza",
        "title": "travel guide to italy",
        "discription": "places you should visit"
    },
    "5": {
        "auther": "narges",
        "title": "photography basics",
        "discription": "learn composition and lighting"
    },
    "6": {
        "auther": "hossein",
        "title": "fitness for everyone",
        "discription": "home workout routines"
    },
    "7": {
        "auther": "fateme",
        "title": "book recommendations",
        "discription": "best novels of the year"
    },
    "8": {
        "auther": "amir",
        "title": "gaming setup guide",
        "discription": "build your dream gaming pc"
    },
    "9": {
        "auther": "leila",
        "title": "meditation for stress",
        "discription": "calm your mind in 10 minutes"
    },
    "10": {
        "auther": "mehdi",
        "title": "web development trends",
        "discription": "what's new in 2026"
    },
    "11": {
        "auther": "shirin",
        "title": "baking for beginners",
        "discription": "easy cake and cookie recipes"
    }
}


@app.get("/")
def home():
    return {"isworking": "True"}


@app.get("/posts")
def get_all_posts():
    return text_posts


@app.get("/posts/get/{id}")
def get_post_by_id(id: str) -> PostModel:
    if id not in text_posts:
        raise HTTPException(404, detail="post not found")
    return text_posts.get(id)


@app.get("/posts/get")
def get_post_by_limit(lenght: int = None):
    if lenght:
        return list(text_posts.values())[:lenght]
    else:
        return text_posts


@app.post("/posts/")
def add_new_post(post: PostModel) -> PostModel:
    index = len(text_posts.keys())+1
    text_posts[index] = {
        "auther": post.auther,
        "title": post.title,
        "discription": post.discription
    }
    return text_posts


@app.post("/upload")
async def uploadfile(
        file: UploadFile = File(...),
        caption: str = Form(""),
        session: AsyncSession = Depends(get_async_session)
):
    pass
