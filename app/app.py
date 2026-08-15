import shutil
import os
import uuid
import tempfile


from fastapi import FastAPI, HTTPException, Form, File, UploadFile, Depends
from app.models import PostModel, PostImages, Posts
from app.core.db import creat_db_and_table, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit


@asynccontextmanager
async def lifespan(app: FastAPI):
    await creat_db_and_table()
    yield

app = FastAPI(lifespan=lifespan)


@app.get("/")
def home():
    return {"isworking": "True"}


@app.get("/posts/get/all")
async def get_post_all(db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(Posts))
    posts = [row[0] for row in result.all()]
    post_data = []
    for post in posts:
        post_data.append({
            "id": post.id,
            "auther": post.auther,
            "title": post.title,
            "discription": post.discription
        })
    return {"posts": post_data}


@app.get("/posts/get/id")
async def get_post_id(id: str, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(Posts))
    posts = [row[0] for row in result.all()]
    for post in posts:
        if str(post.id) == id:
            return {"post": post}


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

    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        with open(temp_file_path, "rb") as filepath:
            rps = imagekit.files.upload(
                file=filepath, file_name=file.filename)

        # TODO: add thumbnale url
        post = PostImages(
            caption=dis,
            file_type=rps.file_type,
            file_name=rps.name,
            url=rps.url
        )

        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()


@app.get("/posts/get/images/all")
async def get_all_images(
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(PostImages))
    posts = [row[0] for row in result.all()]
    post_data = []
    for post in posts:
        post_data.append({
            "id": str(post.id),
            "caption": post.caption,
            "url": post.url,
            "filename": post.file_name,
            "filetype": post.file_type,
            "Date": post.Date
        })

    return {"posts": post_data}
