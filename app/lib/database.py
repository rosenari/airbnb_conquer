import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, async_scoped_session
from sqlalchemy.orm import declarative_base
from app.config import DB_USER, DB_PASSWORD, DB_NAME, DB_HOST
import os


SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL",
                                    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")


async_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True
)


session_factory = async_sessionmaker(bind=async_engine)
Session = async_scoped_session(session_factory, scopefunc=asyncio.current_task)  # task 별로 세션을 관리함.

Base = declarative_base()


async def get_db():
    async with Session() as session:  # async 세션을 사용
        yield session
    await Session.remove()
    await async_engine.dispose()