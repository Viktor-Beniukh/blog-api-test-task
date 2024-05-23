from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.conf.utils import get_app_env


class Settings(BaseSettings):
    api_v1_prefix: str = "/api/v1"
    database_url: str
    secret_key: str
    jwt_secret_key: str
    algorithm: str
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7

    model_config = SettingsConfigDict(env_file=get_app_env(), extra="allow")


settings = Settings()
