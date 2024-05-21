import logging

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import models
from src.schemas.authors import AuthorCreate, AuthorChangeRole
from src.services.security import get_password_hash
from src.services.validation import validate_password

logger = logging.getLogger(__name__)


async def create_author(author: AuthorCreate, session: AsyncSession) -> JSONResponse | models.Author:
    try:
        validate_password(password=author.password)
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return JSONResponse(content={"error": str(ve)}, status_code=422)

    hashed_password = get_password_hash(password=author.password)

    new_author = models.Author(
        email=author.email, username=author.username, hashed_password=hashed_password,
    )

    session.add(new_author)

    await session.commit()
    await session.refresh(new_author)

    return new_author


async def get_author_by_email(email: str, session: AsyncSession) -> models.Author | None:
    stmt = select(models.Author).where(models.Author.email == email)
    result: Result = await session.execute(stmt)
    author_data = result.scalar_one_or_none()
    return author_data


async def get_author_by_id(author_id: int, session: AsyncSession) -> models.Author | None:
    stmt = select(models.Author).where(models.Author.id == author_id)
    result: Result = await session.execute(stmt)
    author_data = result.scalar_one_or_none()
    return author_data


async def update_token(author: models.Author, refresh_token: str | None, session: AsyncSession) -> None:
    """
    The update_token function updates the refresh token for a user.

    Arguments:
        author (Author): Pass the user object to the function
        refresh_token (str | None): Pass the refresh token to the update_token function
        session (AsyncSession): SQLAlchemy session object for accessing the database

    Returns:
        None
    """
    author.refresh_token = refresh_token

    await session.commit()


async def change_author_role(author_role: AuthorChangeRole, session: AsyncSession) -> models.Author:
    """
    Logged-in admin can change role of any profile by ID.

    Arguments:
        author_role (AuthorChangeRole): A set of user new role
        session (AsyncSession): SQLAlchemy session object for accessing the database

    Returns:
        Author: An author object
    """
    author_to_update = await get_author_by_id(author_id=author_role.id, session=session)

    if not author_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")

    author_to_update.role = author_role.role

    await session.commit()

    return author_to_update


async def change_password(email: str, password: str, session: AsyncSession) -> None:
    author = await get_author_by_email(email=email, session=session)

    author.hashed_password = password

    await session.commit()
