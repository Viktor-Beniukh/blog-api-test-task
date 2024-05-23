import os


def get_app_env():
    app_env = os.getenv("APP_ENV", "dev")

    if app_env == "prod":
        return ".env"
    else:
        return ".env.local"
