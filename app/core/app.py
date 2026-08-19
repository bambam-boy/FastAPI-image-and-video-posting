import os
import json

from fastapi import FastAPI, HTTPException, File, UploadFile, Depends
from app.models.PostModels import Posts
from app.database.db import creat_db_and_table, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.core.user import auth_backend, current_active_user, fastapi_user
from app.models.schemas import UserCreat, UserRead, UserUpdate
from app.models.UserModels import User
from app.utils.utils import get_image_from_file
from redis.asyncio import Redis
from fastapi.encoders import jsonable_encoder


@asynccontextmanager
async def lifespan(app: FastAPI):
    await creat_db_and_table()
    app.state.redis = Redis(host="localhost", port=6379, protocol=2)
    yield
    await app.state.redis.close()

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

is_anychanges = True


@app.get("/")
def home():
    return {"fastapi": "postingProject"}


@app.get("/posts/get")
async def get_all_posts(db: AsyncSession = Depends(get_async_session)):
    global is_anychanges
    values = await app.state.redis.get("posts")
    if is_anychanges or values is None:
        resoult = await db.execute(select(Posts))
        resout_value = resoult.scalars().all()
        converted_value = jsonable_encoder(resout_value)
        posts = {"posts": converted_value}
        await app.state.redis.set("posts", json.dumps(posts))
        is_anychanges = False
        return posts
    else:
        return json.loads(values)


@app.get("/posts/get/{id}")
async def get_post_by_id(id: str, db: AsyncSession = Depends(get_async_session)):
    values = app.state.redis.get("posts")
    value = json.loads(values)["posts"].get(id)
    if not value:
        raise HTTPException(status_code=404, detail="post not found")
    return value


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
        rps = get_image_from_file(file)
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
        global is_anychanges
        if not is_anychanges:
            is_anychanges = True
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()


@app.delete("/posts/delete/{id}")
async def delete_post_by_id(
    id: str,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        global is_anychanges
        if not is_anychanges:
            is_anychanges = True


@app.put("/posts/update/{id}")
async def update_post_by_id(
    id: str, title: str | None = "",
    discription: str | None = "",
    file: UploadFile = File(None),
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    try:
        result = await db.execute(select(Posts).where(id == Posts.id))
        post = result.scalars().first()
        if user.id == post.user_id:
            if not post:
                raise HTTPException(status_code=404, detail="post not found")
            post.title = title
            post.discription = discription
            if file:
                rps = get_image_from_file(file)
                post.url = rps.url
            await db.commit()
            return post
        else:
            raise HTTPException(
                status_code=403, detail="you dont have permision to delete this post")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        global is_anychanges
        if not is_anychanges:
            is_anychanges = True
