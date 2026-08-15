from fastapi import FastAPI, HTTPException, Form, File, UploadFile, Depends
from app.models import PostModel, PostImages, Posts
from app.core.db import creat_db_and_table, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select


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


@app.get("/posts/get/all")
async def get_all_posts(db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(Posts))
    posts = [row[0] for row in result.all()]
    post_data = []
    for post in posts:
        post_data.append({
            "auther": post.auther,
            "title": post.title,
            "discription": post.discription
        })
    return {"posts": post_data}


# @app.get("/posts/get/{id}")
# def get_post_by_id(id: str) -> PostModel:
#     if id not in text_posts:
#         raise HTTPException(404, detail="post not found")
#     return text_posts.get(id)


# @app.get("/posts/get")
# def get_post_by_limit(lenght: int = None):
#     if lenght:
#         return list(text_posts.values())[:lenght]
#     else:
#         return text_posts


@app.post("/posts/new")
async def add_new_post(
    user_auther: str,
    user_title: str,
    dis: str,
    db: AsyncSession = Depends(get_async_session)
):
    post = Posts(
        auther=user_auther,
        title=user_title,
        discription=dis,
    )

    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


@app.post("/posts/upload")
async def uploadimage(
        file: UploadFile = File(...),
        dis: str = Form(""),
        session: AsyncSession = Depends(get_async_session)
):
    post = PostImages(
        caption=dis,
        file_type="photo",
        file_name="someting"
    )

    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post


@app.get("/posts/get/date")
async def get_feed(
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(PostImages).order_by(PostImages.Date.desc()))
    posts = [row[0] for row in result.all()]
    post_data = []
    for post in posts:
        post_data.append({
            "id": str(post.id),
            "caption": post.caption
        })

    return {"posts": post_data}
