from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from app.core.settings import settings

engine: AsyncEngine = create_async_engine(settings.db_url, echo=True)


async def init_db() -> None:
    async with engine.begin() as conn:
        # this runs CREATE TABLE IF NOT EXISTS for all models
        await conn.run_sync(SQLModel.metadata.create_all)