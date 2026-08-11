from collections.abc import AsyncGenerator


from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.models import DataBaseModel

USERNAME = "postgres"
PASSWORD = "lokihoo88"
HOST = "localhost"
PORT = "5432"
DB_NAME = "fastapipostingdb"

DATABASE_URL = f"postgresql+asyncpg://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

engin = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engin, expire_on_commit=False)


async def creat_db_and_table():
    async with engin.begin() as connection:
        await connection.run_sync(DataBaseModel.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
