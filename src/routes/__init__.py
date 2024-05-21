from fastapi import APIRouter

from src.routes.categories import router as categories_router
from src.routes.posts import router as posts_router


router = APIRouter()


router.include_router(router=categories_router, prefix="/categories")
router.include_router(router=posts_router, prefix="/posts")
