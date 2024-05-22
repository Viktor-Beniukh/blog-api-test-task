from fastapi import HTTPException, status

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import models
from src.schemas.tags import TagUpdate


async def create_tag(session: AsyncSession, tag_name: str) -> models.Tag:
    new_tag = models.Tag(name=tag_name)

    session.add(new_tag)

    await session.commit()
    await session.refresh(new_tag)

    return new_tag


async def get_tag_by_id(session: AsyncSession, tag_id: int) -> models.Tag | None:
    stmt = select(models.Tag).where(models.Tag.id == tag_id)
    result: Result = await session.execute(stmt)
    tag = result.scalar_one_or_none()
    return tag


async def get_tag_by_name(session: AsyncSession, tag_name: str) -> models.Tag | None:
    stmt = select(models.Tag).where(models.Tag.name == tag_name)
    result: Result = await session.execute(stmt)
    tag = result.scalar_one_or_none()
    return tag


async def update_tag(
    session: AsyncSession, tag_id: int, tag_update: TagUpdate
) -> models.Tag:
    db_tag = await get_tag_by_id(tag_id=tag_id, session=session)

    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )

    db_tag.name = tag_update.name

    await session.commit()
    await session.refresh(db_tag)

    return db_tag


async def delete_tag(session: AsyncSession, tag_id: int) -> None:
    db_tag = await get_tag_by_id(tag_id=tag_id, session=session)

    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )

    await session.delete(db_tag)
    await session.commit()
