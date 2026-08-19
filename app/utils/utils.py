import os
import shutil
import tempfile

from fastapi import UploadFile, File, FastAPI, Depends
from app.database.db import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.images import imagekit


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


async def add_new_value_to_redis(app: FastAPI, db: AsyncSession = Depends(get_async_session)):
    values = await app.state.redis.delete("posts")
