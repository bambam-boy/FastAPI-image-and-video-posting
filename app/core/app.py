import shutil
import os
import uuid
import tempfile


from fastapi import FastAPI, HTTPException, Form, File, UploadFile, Depends
from app.models.PostModels import PostImages, Posts
from app.database.db import creat_db_and_table, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.core.images import imagekit
from app.core.user import auth_backend, current_active_user, fastapi_user
from app.models.schemas import UserCreat, UserRead, UserUpdate
from app.models.UserModels import User


@asynccontextmanager
async def lifespan(app: FastAPI):
    await creat_db_and_table()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(fastapi_user.get_auth_router(
    auth_backend), prefix="/auth/jwt", tags=["auth"])
app.include_router(fastapi_user.get_register_router(UserRead, UserCreat),
                   prefix="/auth", tags=["auth"])
app.include_router(fastapi_user.get_reset_password_router(),
                   prefix="/auth", tags=["auth"])
app.include_router(fastapi_user.get_verify_router(
    UserRead), prefix="/auth", tags=["auth"])
app.include_router(fastapi_user.get_users_router(
    UserRead, UserUpdate), prefix="/auth", tags=["auth"])


@app.get("/")
def home():
    return {"fastapi": "postingProject"}


@app.get("/posts/get/all")
async def get_post_all(
    db: AsyncSession = Depends(get_async_session),
):
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
async def get_post_id(id: str, db: AsyncSession = Depends(get_async_session),    user: User = Depends(current_active_user)):
    result = await db.execute(select(Posts))
    posts = [row[0] for row in result.all()]
    for post in posts:
        if str(post.id) == id:
            return {"post": post}


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


@app.post("/posts/add/textpost")
async def add_new_post(
    user_auther: str,
    user_title: str,
    dis: str,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    post = Posts(
        auther=user_auther,
        title=user_title,
        discription=dis,
        user_id=user.id
    )

    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


@app.post("/posts/add/imagepost")
async def uploadimage(
        user: User = Depends(current_active_user),
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


@app.delete("/posts/delete/images/{id}")
async def delete_imagepost_id(id: str, user: User = Depends(current_active_user), db: AsyncSession = Depends(get_async_session)):
    try:
        response = await db.execute(select(PostImages).where(uuid.UUID(id) == PostImages.id))
        post = response.scalars().first()

        if not post:
            raise HTTPException(status_code=404, detail="pos not found")

        await db.delete(post)
        await db.commit()
        return {"success": "post deleted"}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


@app.delete("/posts/delete/text/{id}")
async def delete_textpost_id(id: str, user: User = Depends(current_active_user), db: AsyncSession = Depends(get_async_session)):
    try:
        response = await db.execute(select(Posts).where(uuid.UUID(id) == Posts.id))
        post = response.scalars().first()
        if post.user_id == user.id:
            if not post:
                raise HTTPException(status_code=404, detail="post not found")

            await db.delete(post)
            await db.commit()
            return {"success": "text post deleted success fully"}
        else:
            raise HTTPException(
                status_code=401, detail="you dont have access to delete this post")
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
