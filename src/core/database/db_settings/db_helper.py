import logging

from typing import AsyncGenerator, Annotated

from fastapi import HTTPException, status, Depends

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.core.conf.config import settings

logger = logging.getLogger(__name__)


SQLALCHEMY_DATABASE_URL = settings.database_url

async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

async_session = async_sessionmaker(
    bind=async_engine, autoflush=False, autocommit=False, expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        except SQLAlchemyError as err_sql:
            logger.exception("SQLAlchemyError")
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(err_sql)
            )


db_dependency = Annotated[AsyncSession, Depends(get_async_session)]
