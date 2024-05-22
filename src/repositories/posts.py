import os
from datetime import datetime

from io import BytesIO
from PIL import Image

from fastapi import HTTPException, status, UploadFile

from sqlalchemy import select, desc, and_
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import subqueryload, joinedload

from src.core.database import models
from src.core.database.models.post_tag_association import post_tag_association_table
from src.core.database.models.utils import slugify

from src.schemas.posts import PostCreate, PostPartialUpdate

from src.repositories import tags as repository_tags


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


async def add_tags_to_post(
    post_id: int, author_id: int, tag_names: list[str], session: AsyncSession
) -> None:
    post = await get_post_by_id_and_by_author_id(post_id=post_id, author_id=author_id, session=session)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    for tag_name in tag_names:
        tag_name = models.Tag.add_hashtag(tag_name)
        tag = await repository_tags.get_tag_by_name(session=session, tag_name=tag_name)
        if tag is None:
            tag = await repository_tags.create_tag(session=session, tag_name=tag_name)

        post_tag_association = post_tag_association_table.insert().values(
            post_id=post.id, tag_id=tag.id
        )
        await session.execute(post_tag_association)

    await session.commit()


async def remove_tag_from_post(session: AsyncSession, tag_id: int, post_id: int, author_id: int) -> None:
    post = await get_post_by_id_and_by_author_id(post_id=post_id, author_id=author_id, session=session)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    tag = await repository_tags.get_tag_by_id(session=session, tag_id=tag_id)

    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    association_record = await session.execute(
        select(post_tag_association_table)
        .filter(
            post_tag_association_table.c.post_id == post.id,
            post_tag_association_table.c.tag_id == tag.id
        )
    )
    association_record = association_record.scalar_one_or_none()

    if not association_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Association between post and tag not found"
        )

    post_tag_association = post_tag_association_table.delete().where(
        and_(
            post_tag_association_table.c.post_id == post.id,
            post_tag_association_table.c.tag_id == tag.id
        )
    )

    await session.execute(post_tag_association)
    await session.commit()


async def get_all_posts(session: AsyncSession) -> list[models.Post]:
    stmt = (
        select(models.Post)
        .options(joinedload(models.Post.author).joinedload(models.Author.profile))
        .options(subqueryload(models.Post.tags))
        .order_by(desc(models.Post.created_at))
    )
    result: Result = await session.execute(stmt)
    posts = result.scalars().all()
    return list(posts)


async def get_all_posts_by_author_id(author_id: int, session: AsyncSession) -> list[models.Post]:
    stmt = (
        select(models.Post)
        .options(subqueryload(models.Post.tags))
        .where(models.Post.author_id == author_id)
        .order_by(desc(models.Post.created_at))
    )
    result: Result = await session.execute(stmt)
    posts = result.scalars().all()
    return list(posts)


async def get_all_posts_by_category_id(category_id: int, session: AsyncSession) -> list[models.Post]:
    stmt = (
        select(models.Post)
        .options(joinedload(models.Post.author).joinedload(models.Author.profile))
        .options(subqueryload(models.Post.tags))
        .where(models.Post.category_id == category_id)
        .order_by(desc(models.Post.created_at))
    )
    result: Result = await session.execute(stmt)
    posts = result.scalars().all()
    return list(posts)


async def get_specific_post_by_id(session: AsyncSession, post_id: int) -> models.Post | None:
    stmt = (
        select(models.Post)
        .options(subqueryload(models.Post.tags))
        .where(models.Post.id == post_id)
        .order_by(desc(models.Post.created_at))
    )
    result: Result = await session.execute(stmt)
    post = result.scalar_one_or_none()
    return post


async def get_single_post_by_slug(session: AsyncSession, slug: str) -> models.Post | None:
    stmt = (
        select(models.Post)
        .options(joinedload(models.Post.author).joinedload(models.Author.profile))
        .options(subqueryload(models.Post.tags))
        .where(models.Post.slug == slug)
        .order_by(desc(models.Post.created_at))
    )
    result: Result = await session.execute(stmt)
    post = result.scalar_one_or_none()
    return post


async def get_post_by_id_and_by_author_id(
    session: AsyncSession, post_id: int, author_id: int
) -> models.Post | None:
    stmt = (
        select(models.Post)
        .options(subqueryload(models.Post.tags))
        .where(
            models.Post.author_id == author_id,
            models.Post.id == post_id
        )
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
