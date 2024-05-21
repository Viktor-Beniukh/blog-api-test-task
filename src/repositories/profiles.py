import os
import logging

from io import BytesIO
from PIL import Image

from fastapi import UploadFile
from fastapi.responses import JSONResponse

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import models

from src.repositories import authors as repository_authors

from src.schemas.profiles import ProfileCreate, ProfilePartialUpdate

from src.services.validation import validate_phone_number

logger = logging.getLogger(__name__)


async def create_profile(
    profile: ProfileCreate, author_id: int, session: AsyncSession
) -> JSONResponse | models.Profile:
    author = await repository_authors.get_author_by_id(author_id=author_id, session=session)

    try:
        validate_phone_number(phone_number=profile.phone_number)
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return JSONResponse(content={"error": str(ve)}, status_code=422)

    new_profile = models.Profile(**profile.model_dump(), author_id=author.id)

    session.add(new_profile)

    await session.commit()
    await session.refresh(new_profile)

    return new_profile


async def get_profile_by_author_id(author_id: int, session: AsyncSession) -> models.Profile | None:
    stmt = select(models.Profile).where(models.Profile.author_id == author_id)
    result: Result = await session.execute(stmt)
    existing_profile = result.scalar_one_or_none()
    return existing_profile


async def partial_update_profile(
    updated_profile: ProfilePartialUpdate, author_id: int, session: AsyncSession,
) -> JSONResponse | models.Profile:
    author = await repository_authors.get_author_by_id(author_id=author_id, session=session)
    profile = await get_profile_by_author_id(author_id=author.id, session=session)

    try:
        validate_phone_number(phone_number=updated_profile.phone_number)
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return JSONResponse(content={"error": str(ve)}, status_code=422)

    update_data = updated_profile.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(profile, field, value)

    await session.commit()
    await session.refresh(profile)

    return profile


async def upload_profile_image(
        file: UploadFile, profile: models.Profile, session: AsyncSession
) -> None:
    media_dir = "media"
    os.makedirs(media_dir, exist_ok=True)

    uploads_dir = os.path.join(media_dir, "uploads")
    os.makedirs(uploads_dir, exist_ok=True)

    image = Image.open(BytesIO(await file.read()))

    file_extension = file.filename.split(".")[-1]

    filename = f"{profile.author.username}_profile_image.{file_extension}"
    filepath = os.path.join(uploads_dir, filename.lower())

    image.save(filepath)

    profile.image = filename.lower()

    await session.commit()
    await session.refresh(profile)


async def delete_profile(author_id: int, session: AsyncSession) -> None:
    author = await repository_authors.get_author_by_id(author_id=author_id, session=session)
    profile = await get_profile_by_author_id(author_id=author.id, session=session)

    await session.delete(profile)
    await session.commit()
