import shutil
import os
import uuid
import tempfile


from fastapi import FastAPI, HTTPException, Form, File, UploadFile, Depends
from app.models.PostModels import Posts
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
    UserRead, UserUpdate), prefix="/auth", tags=["users"])


@app.get("/")
def home():
    return {"fastapi": "postingProject"}


@app.get("/posts/get")
async def get_all_posts(db: AsyncSession = Depends(get_async_session)):
    resoult = await db.execute(select(Posts))
    posts = [row[0] for row in resoult.all()]
    posts_data = []
    for post in posts:
        posts_data.append(post)
    return posts_data


@app.post("/posts/add")
async def add_new_post(
        title: str,
        dis: str,
        user: User = Depends(current_active_user),
        file: UploadFile = File(...),
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
        post = Posts(
            user_id=user.id,
            auther=user.username,
            title=title,
            discription=dis,
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


@app.delete("/posts/delete/{id}")
async def delete_post_by_id(
    id: str,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    result = await db.execute(select(Posts).where(id == Posts.id))
    post = result.scalars().first()

    if post.user_id == user.id:
        if not post:
            raise HTTPException(status_code=404, detail="post not found")
        await db.delete(post)
        await db.commit()
        return {"success": "true"}
    else:
        raise HTTPException(
            status_code=403, detail="you dont have permision to delete this post")
