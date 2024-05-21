import logging

from fastapi import APIRouter, status, HTTPException, Depends, UploadFile
from fastapi.responses import JSONResponse

from src.core.database.db_settings.db_helper import db_dependency
from src.core.database.models import Author, Profile
from src.core.database.models.enums import Role

from src.schemas.profiles import ProfileResponse, ProfileCreate, ProfilePartialUpdate
from src.schemas.authors import (
    AuthorResponse, AuthorMessageResponse, PasswordChangeModel, AuthorChangeRole,
)

from src.services.auth import auth_service
from src.services.roles import RoleAccess
from src.services.security import verify_password, get_password_hash
from src.services.validation import validate_password, validate_image

from src.repositories import authors as repository_authors
from src.repositories import profiles as repository_profiles

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/authors", tags=["Authors"])

allowed_operation_admin = RoleAccess([Role["admin"]])


@router.get("/me", response_model=AuthorResponse)
async def read_authors_me(current_author: Author = Depends(auth_service.get_current_author)) -> Author:
    """
    The read_authors_me function is a GET request that returns the current author's information.
        It requires authentication, and it uses the auth_service to get the current author.

        Arguments:
            current_author (Author): the current author

    Returns:
        Author: The current author object
    """
    return current_author


@router.post("/me/change_password", response_model=AuthorMessageResponse)
async def change_password(
    body: PasswordChangeModel,
    session: db_dependency,
    current_author: Author = Depends(auth_service.get_current_author),
) -> JSONResponse | dict[str, str]:
    """
    The change_password function takes a body as input.

    The body contains the new password for that user,
    which is hashed using pwd_context.hash() before being stored in
    the database.

        Args:
            body: PasswordChangeModel: Get the password from the request body
            session: db_dependency: Get the database session
            current_author (Author): the current author

    Returns:
        A message to the author
    """
    author = await repository_authors.get_author_by_email(email=current_author.email, session=session)

    if author is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )

    if not verify_password(plain_password=body.old_password, hashed_password=author.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password"
        )

    try:
        validate_password(password=body.new_password)
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return JSONResponse(content={"error": str(ve)}, status_code=422)

    if body.new_password != body.new_password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The new password and confirmed new password must be equal!"
        )

    body.new_password = get_password_hash(password=body.new_password)

    await repository_authors.change_password(
        email=author.email, password=body.new_password, session=session
    )

    return {"message": "Your password changed successfully"}


@router.post("/me/profile", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_author_profile(
    author_profile: ProfileCreate,
    session: db_dependency,
    current_author: Author = Depends(auth_service.get_current_author),
) -> Profile:
    """
    The create_author_profile function creates a new profile for current author in the database.
    It takes a ProfileCreate object as input, and returns the newly created author profile.

        Args:
            author_profile: ProfileCreate: Receive the data of the author profile to be created
            session: db_dependency: Access the database
            current_author (Author): the current author

    Returns:
        The created author profile
    """
    existing_profile = await repository_profiles.get_profile_by_author_id(
        author_id=current_author.id, session=session
    )

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Profile for this author already exists",
        )

    new_profile = await repository_profiles.create_profile(
        profile=author_profile, author_id=current_author.id, session=session
    )

    return new_profile


@router.patch("/me/profile", response_model=ProfileResponse)
async def partial_update_author_profile(
    author_profile: ProfilePartialUpdate,
    session: db_dependency,
    current_author: Author = Depends(auth_service.get_current_author),
) -> Profile:
    """
    The partial_update_author_profile function partial updates a profile data for current author in the database.
    It takes a ProfilePartialUpdate object as input, and returns the newly partial updated author profile.

        Args:
            author_profile: ProfilePartialUpdate: Receive the data of the author profile to be updated
            session: db_dependency: Access the database
            current_author (Author): the current author

    Returns:
        The updated author profile
    """
    existing_profile = await repository_profiles.get_profile_by_author_id(
        author_id=current_author.id, session=session
    )

    if not existing_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Author profile not found",
        )

    partial_updated_user_profile = await repository_profiles.partial_update_profile(
        updated_profile=author_profile, author_id=current_author.id, session=session
    )

    return partial_updated_user_profile


@router.delete("/me/profile", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author_profile(
    session: db_dependency, current_author: Author = Depends(auth_service.get_current_author)
) -> None:
    """
    The delete_author_profile function removes a profile data for current author in the database.

        Args:
            session: db_dependency: Access the database
            current_author (Author): the current author

    Returns:
        None
    """
    existing_profile = await repository_profiles.get_profile_by_author_id(
        author_id=current_author.id, session=session
    )

    if not existing_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Author profile not found",
        )

    await repository_profiles.delete_profile(author_id=current_author.id, session=session)


@router.post("/me/profile/upload-image", response_model=AuthorMessageResponse)
async def upload_profile_image(
    session: db_dependency,
    file: UploadFile = Depends(validate_image),
    current_author: Author = Depends(auth_service.get_current_author),
) -> dict[str, str]:
    existing_profile = await repository_profiles.get_profile_by_author_id(
        author_id=current_author.id, session=session
    )

    if not existing_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Author profile not found",
        )

    await repository_profiles.upload_profile_image(
        file=file, profile=existing_profile, session=session
    )

    return {"message": "Profile image uploaded successfully"}


@router.put("/change_role", response_model=AuthorResponse,
            dependencies=[Depends(allowed_operation_admin)])
async def change_role(author_role: AuthorChangeRole, session: db_dependency) -> Author:
    """
    Change the role of an author

        Arguments:
            author_role (AuthorChangeRole): object with new role
            (role: (permitted: "admin", "moderator", "user"))
            session (db_dependency): SQLAlchemy session object for accessing the database

    Returns:
        Author: object after the change operation
    """

    return await repository_authors.change_author_role(author_role=author_role, session=session)
