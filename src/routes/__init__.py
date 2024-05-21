from fastapi import APIRouter

from src.routes.categories import router as categories_router


router = APIRouter()


router.include_router(router=categories_router, prefix="/categories")
