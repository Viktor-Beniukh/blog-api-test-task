import os
from datetime import datetime

from io import BytesIO
from PIL import Image

from fastapi import HTTPException, status, UploadFile

from sqlalchemy import select, desc
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import models
from src.core.database.models.utils import slugify
from src.schemas.posts import PostCreate, PostPartialUpdate


async def create_post(
    post_data: PostCreate, author_id: int, category_id: int, session: AsyncSession
) -> models.Post:
    new_post = models.Post(**post_data.model_dump(), author_id=author_id, category_id=category_id)

    session.add(new_post)

    await session.commit()
    await session.refresh(new_post)

    new_post.slug = f"{new_post.slug}-{new_post.category.slug}-{new_post.id}"

    await session.commit()

    return new_post


async def get_all_posts(session: AsyncSession) -> list[models.Post]:
    stmt = select(models.Post).order_by(desc(models.Post.created_at))
    result: Result = await session.execute(stmt)
    posts = result.scalars().all()
    return list(posts)


async def get_all_posts_by_author_id(author_id: int, session: AsyncSession) -> list[models.Post]:
    stmt = (
        select(models.Post)
        .where(models.Post.author_id == author_id)
        .order_by(desc(models.Post.created_at))
    )
    result: Result = await session.execute(stmt)
    posts = result.scalars().all()
    return list(posts)


async def get_specific_post_by_id(session: AsyncSession, post_id: int) -> models.Post | None:
    stmt = (
        select(models.Post)
        .where(models.Post.id == post_id)
        .order_by(desc(models.Post.created_at))
    )
    result: Result = await session.execute(stmt)
    post = result.scalar_one_or_none()
    return post


async def get_post_by_id_and_by_author_id(
    session: AsyncSession, post_id: int, author_id: int
) -> models.Post | None:
    stmt = select(models.Post).where(
        models.Post.author_id == author_id,
        models.Post.id == post_id
    )
    result: Result = await session.execute(stmt)
    post = result.scalar_one_or_none()
    return post


async def partial_update_post(
    session: AsyncSession, post_update: PostPartialUpdate, post_id: int,  author_id: int
) -> models.Post:
    post = await get_post_by_id_and_by_author_id(
        session=session, post_id=post_id, author_id=author_id
    )
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    update_data = post_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(post, field, value)

    post.slug = f"{slugify(post_update.title).lower()}-{post.category.slug}-{post.id}"
    post.updated_at = datetime.now()

    await session.commit()
    await session.refresh(post)

    return post


async def delete_post(session: AsyncSession, post_id: int, author_id: int) -> None:
    post = await get_post_by_id_and_by_author_id(
        session=session, post_id=post_id, author_id=author_id
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    await session.delete(post)
    await session.commit()


async def upload_post_image(file: UploadFile, post: models.Post, session: AsyncSession) -> None:
    media_dir = "media"
    os.makedirs(media_dir, exist_ok=True)

    posts_dir = os.path.join(media_dir, "posts")
    os.makedirs(posts_dir, exist_ok=True)

    image = Image.open(BytesIO(await file.read()))

    file_extension = file.filename.split(".")[-1]

    filename = f"{post.slug}_post_image.{file_extension}"
    filepath = os.path.join(posts_dir, filename.lower())

    image.save(filepath)

    post.image = filename.lower()
    post.updated_at = datetime.now()

    await session.commit()
    await session.refresh(post)
