from fastapi import HTTPException, status

from sqlalchemy import select, asc
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import models
from src.core.database.models.utils import slugify
from src.schemas.categories import CategoryChange


async def create_category(category: CategoryChange, session: AsyncSession) -> models.Category:

    new_category = models.Category(**category.model_dump())

    session.add(new_category)

    await session.commit()
    await session.refresh(new_category)

    return new_category


async def get_all_categories(session: AsyncSession) -> list[models.Category]:
    stmt = select(models.Category).order_by(asc(models.Category.name))
    result: Result = await session.execute(stmt)
    categories = result.scalars().all()
    return list(categories)


async def get_category_by_id(session: AsyncSession, category_id: int) -> models.Category | None:
    stmt = select(models.Category).where(models.Category.id == category_id)
    result: Result = await session.execute(stmt)
    category = result.scalar_one_or_none()
    return category


async def get_category_by_id_and_slug(
        session: AsyncSession, category_id: int, category_slug: str
) -> models.Category | None:
    stmt = select(models.Category).where(
        models.Category.id == category_id,
        models.Category.slug == category_slug
    )
    result: Result = await session.execute(stmt)
    category = result.scalar_one_or_none()
    return category


async def get_category_by_name(session: AsyncSession, category_name: str) -> models.Category | None:
    stmt = select(models.Category).where(models.Category.name == category_name)
    result: Result = await session.execute(stmt)
    category = result.scalar_one_or_none()
    return category


async def update_category(
    updated_category: CategoryChange, category_id: int, session: AsyncSession
) -> models.Category:
    category = await get_category_by_id(category_id=category_id, session=session)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found",
        )

    update_data = updated_category.model_dump()

    for field, value in update_data.items():
        setattr(category, field, value)

    category.slug = slugify(updated_category.name).lower()

    await session.commit()
    await session.refresh(category)

    return category


async def delete_category(category_id: int, session: AsyncSession) -> None:
    category = await get_category_by_id(category_id=category_id, session=session)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found",
        )

    await session.delete(category)
    await session.commit()
