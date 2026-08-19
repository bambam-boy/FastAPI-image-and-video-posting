import os
import shutil
import json
import tempfile

from fastapi import UploadFile, File, FastAPI, Depends
from fastapi.encoders import jsonable_encoder
from app.database.db import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.PostModels import Posts
from app.core.images import imagekit


async def add_new_value_to_redis(
    is_prop_created: bool,
    prop_title: str, app: FastAPI,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        if not is_prop_created:
            await app.state.redis.get(prop_title)
        datas = await db.execute(select(Posts))
        posts_database_base = datas.scalars().all()
        posts_encoded = jsonable_encoder(posts_database_base)
        posts = {"posts": posts_encoded}
        posts_json = json.dumps(posts)
        await app.state.redis.set(prop_title, posts_json)
        return posts_json
    except Exception as e:
        raise Exception(e)


def get_image_from_file(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        with open(temp_file_path, "rb") as filepath:
            rps = imagekit.files.upload(
                file=filepath, file_name=file.filename)
        return rps
    except Exception as e:
        raise Exception(e)
