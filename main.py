import logging

import uvicorn

from fastapi import FastAPI
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check

from src.core.conf.config import settings
from src.core.conf.logging_config import setup_logging

from src.routes.auth import router as auth_router
from src.routes.authors import router as authors_router
from src.routes import router as router_v1

setup_logging()

logger = logging.getLogger(__name__)

disable_installed_extensions_check()


app = FastAPI(title="Blog API", description="The management of the Blog API")


app.include_router(router=auth_router, prefix="/api")
app.include_router(router=authors_router, prefix="/api")
app.include_router(router=router_v1, prefix=settings.api_v1_prefix)

add_pagination(app)


@app.get("/", description="Main page")
def read_root():
    """
    Healthcheck page definition

    :return: dict: health status
    """
    logger.info("User accessed the healthcheck page")
    return {"message": "Welcome to FastAPI project"}


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)
