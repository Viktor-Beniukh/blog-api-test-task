from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from src.core.conf.config import settings
from src.core.database.db_settings.db_helper import db_dependency
from src.repositories import authors as repository_authors


class Auth:
    JWT_SECRET_KEY = settings.jwt_secret_key
    ALGORITHM = settings.algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
    REFRESH_TOKEN_EXPIRE_MINUTES = settings.refresh_token_expire_minutes
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/authors/login")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    @classmethod
    def token_decode(cls, token: str) -> dict:
        """
        Try to decode the token

        Arguments:
            token (str): token to take decoded

        Returns:
            dict with results of decoded token
        """
        try:
            return jwt.decode(token, cls.JWT_SECRET_KEY, algorithms=[cls.ALGORITHM])
        except JWTError:
            raise cls.credentials_exception

    @classmethod
    async def create_access_token(
        cls, data: dict, expires_delta: Optional[int] = None
    ) -> str:
        """
        The create_access_token function creates a new access token for the user.
            The function takes in two arguments: data and expires_delta.
            Data is a dictionary that contains all the information about the user,
            such as their username, email address, etc.
            Expires_delta is an optional argument that specifies how long you want your access token to be valid
            for (in seconds). If no value is specified then it defaults to 48 hours.

        Arguments:
            data (dict): A dictionary containing the user's id and username.
            expires_delta (Optional[int]): The number of minutes until the token expires, defaults to None.

        Returns:
            A token that is encoded with the data, current time, expiry time and scope
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(minutes=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(
            to_encode, cls.JWT_SECRET_KEY, algorithm=cls.ALGORITHM
        )
        return encoded_access_token

    @classmethod
    async def create_refresh_token(
        cls, data: dict, expires_delta: Optional[int] = None
    ):
        """
        The create_refresh_token function creates a refresh token for the user.

        Arguments:
            data (dict): A dictionary containing the user's id and username.
            expires_delta (Optional[int]): Set the expiration time of the refresh token

        Returns:
            An encoded refresh token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(minutes=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=cls.REFRESH_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(
            to_encode, cls.JWT_SECRET_KEY, algorithm=cls.ALGORITHM
        )
        return encoded_refresh_token

    @classmethod
    async def decode_refresh_token(cls, refresh_token: str):
        """
        The decode_refresh_token function is used to decode the refresh token.
        It takes a refresh_token as an argument and returns the email of the user if it's valid.
        If not, it raises an HTTPException with status code 401 (UNAUTHORIZED)
        and detail 'Could not validate credentials'.

        Arguments:
            refresh_token (str): Pass the refresh token to the function

        Returns:
            The email of the user that is associated with the refresh token
        """
        payload = cls.token_decode(refresh_token)
        if payload["scope"] == "refresh_token":
            email = payload["sub"]
            return email
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope for token"
        )

    @classmethod
    async def get_current_author(
        cls, session: db_dependency, token: str = Depends(oauth2_scheme)
    ):
        try:
            payload = cls.token_decode(token)
            if payload.get("scope") == "access_token":
                email: str = payload.get("sub")
                if email is None:
                    raise cls.credentials_exception
            else:
                raise cls.credentials_exception

            author = await repository_authors.get_author_by_email(email=email, session=session)
            if author is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Author not found"
                )

            return author

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate token",
            )


auth_service = Auth()
