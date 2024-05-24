from pydantic_settings import BaseSettings, SettingsConfigDict

from db_url import db_url_docker, db_url
from src.core.conf.utils import get_app_env


class Settings(BaseSettings):
    api_v1_prefix: str = "/api/v1"
    database_url: str = db_url_docker if get_app_env() == "prod" else db_url
    secret_key: str = "secret_key"
    jwt_secret_key: str = "jwt_secret_key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7
    redis_host: str = "host_name"
    redis_port: str = "port"

    model_config = SettingsConfigDict(env_file=get_app_env(), extra="allow")


settings = Settings()
