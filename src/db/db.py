from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from src.config import settings

engine = create_async_engine(settings.POSTGRESQL_DB_URL)

SessionLocal = async_sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


async def get_db():
    async with SessionLocal() as db:
        yield db
        await db.commit()
