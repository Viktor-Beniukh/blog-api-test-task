import logging

from fastapi import APIRouter, status, HTTPException, Depends, Response, Request
from fastapi.security import OAuth2PasswordRequestForm

from src.core.database import models
from src.core.database.db_settings.db_helper import db_dependency

from src.schemas.authors import AuthorResponse, AuthorCreate, TokenModel
from src.repositories import authors as repository_authors

from src.services.auth import auth_service
from src.services.security import verify_password


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register",
             response_model=AuthorResponse,
             status_code=status.HTTP_201_CREATED)
async def create_author(author: AuthorCreate, session: db_dependency) -> models.Author:
    """
    The create_user function creates a new user in the database.
        It takes a UserCreate object as input, and returns the newly created user.

        Args:
            author: AuthorCreate: Receive the data of the user to be created
            session: db_dependency: Access the database

    Returns:
        The created author
    """
    author_email = await repository_authors.get_author_by_email(email=author.email, session=session)

    if author_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Author with such email already exists",
        )

    new_author = await repository_authors.create_author(author=author, session=session)

    return new_author


@router.post("/login", response_model=TokenModel)
async def login_for_tokens(
    response: Response,
    session: db_dependency,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> TokenModel:
    """
    The login_for_tokens function is used to receive the refresh_token and the access token.
        The function takes in the user credentials and returns an access_token,
        a refresh_token, and the type of token.

        Arguments:
            response: Response: Sets tokens in cookies
            form_data(OAuth2PasswordRequestForm): enter the user credentials
            session (db_dependency): SQLAlchemy session object for accessing the database

    Returns:
        dict: JSON access_token - refresh_token - token_type - author object
    """

    author = await repository_authors.get_author_by_email(email=form_data.username, session=session)

    if author is None or not verify_password(
        plain_password=form_data.password, hashed_password=author.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid email or password"
        )

    access_token = await auth_service.create_access_token(
        data={"author_id": author.id, "sub": author.email}
    )
    refresh_token_ = await auth_service.create_refresh_token(
        data={"author_id": author.id, "sub": author.email}
    )

    await repository_authors.update_token(author=author, refresh_token=refresh_token_, session=session)

    response.set_cookie(
        key="refresh_token", value=refresh_token_, httponly=True, secure=True, samesite="none"
    )

    return TokenModel(access_token=access_token, token_type="bearer", author=author)


@router.get("/refresh_token", response_model=TokenModel)
async def refresh_token(request: Request, response: Response, session: db_dependency) -> TokenModel:
    """
    The refresh_token function is used to refresh the access token.
        The function takes in a refresh token from cookies and returns an access_token,
        a new refresh_token, and the type of token.
        If the user's current refresh_token does not match what was
            passed into this function then it will return an error.

        Arguments:
            request: Request: Get the token from the Cookie
            response: Response: Sets tokens in cookies
            session (db_dependency): SQLAlchemy session object for accessing the database

    Returns:
        dict: JSON access_token - refresh_token - token_type - author object
    """
    token = request.cookies.get("refresh_token")
    email = await auth_service.decode_refresh_token(refresh_token=token)

    author = await repository_authors.get_author_by_email(email=email, session=session)

    if author.refresh_token != token:
        await repository_authors.update_token(author=author, refresh_token=None, session=session)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    access_token = await auth_service.create_access_token(
        data={"author_id": author.id, "sub": email}
    )
    refresh_token_ = await auth_service.create_refresh_token(
        data={"author_id": author.id, "sub": email}
    )

    await repository_authors.update_token(author=author, refresh_token=refresh_token_, session=session)

    response.set_cookie(
        key="refresh_token", value=refresh_token_, httponly=True, secure=True, samesite="none"
    )

    return TokenModel(access_token=access_token, token_type="bearer", author=author)
