from enum import StrEnum


class Role(StrEnum):
    """
    Roles users.
    """
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"
