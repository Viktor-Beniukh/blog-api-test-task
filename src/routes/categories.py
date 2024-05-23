import pickle

from fastapi import APIRouter, status, HTTPException, Depends
from fastapi_pagination import Page, paginate

from src.core.conf.caching import get_redis
from src.core.database import models
from src.core.database.db_settings.db_helper import db_dependency
from src.core.database.models.enums import Role

from src.repositories import categories as repository_categories
from src.repositories import posts as repository_posts

from src.schemas.categories import CategoryResponse, CategoryChange
from src.schemas.posts import PostTagsResponse

from src.services.cache_in_redis import delete_cache_in_redis
from src.services.roles import RoleAccess

router = APIRouter(tags=["Categories"])

allowed_operation_admin_moderator = RoleAccess([Role["admin"], Role["moderator"]])


@router.post("/",
             response_model=CategoryResponse,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(allowed_operation_admin_moderator)], )
async def create_category(category_data: CategoryChange, session: db_dependency) -> models.Category:
    """
    The create_category function creates a new category in the database.

        Args:
            category_data: CategoryChange: Validate the request body
            session: db_dependency: Pass the database session to the repository layer

    Returns:
        A category object
    """
    category = await repository_categories.get_category_by_name(
        session=session, category_name=category_data.name
    )

    if category:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="The name of the category already exists"
        )

    await delete_cache_in_redis()

    return await repository_categories.create_category(category=category_data, session=session)


@router.get("/",
            response_model=list[CategoryResponse],
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def get_all_categories(session: db_dependency) -> list[models.Category]:
    """
    The function returns a list of all categories in the database.

        Args:
            session: db_dependency: Access the database

    Returns:
        A list of categories
    """

    redis_client = get_redis()

    key = f"categories"

    cached_categories = None

    if redis_client:
        cached_categories = redis_client.get(key)

    if not cached_categories:

        categories = await repository_categories.get_all_categories(session=session)

        if len(categories) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categories not found")

        if redis_client:
            redis_client.set(key, pickle.dumps(categories))
            redis_client.expire(key, 1800)

    else:
        categories = pickle.loads(cached_categories)

    return categories


@router.get("/{category_id}/{category_slug}/posts", response_model=Page[PostTagsResponse])
async def get_single_category_with_posts(
    category_id: int, category_slug: str, session: db_dependency
) -> list[models.Post]:
    """
    The function returns list of posts fot the single category in the database.

        Args:
            category_id: int: Get the id of the category to be obtained
            category_slug: str: Get the slug of the category to be obtained
            session: db_dependency: Access the database

    Returns:
        The category object
    """
    redis_client = get_redis()

    key = f"category_id-{category_id}-category_slug-{category_slug}_posts"

    cached_category_posts = None

    if redis_client:
        cached_category_posts = redis_client.get(key)

    if not cached_category_posts:

        category = await repository_categories.get_category_by_id_and_slug(
            category_id=category_id, category_slug=category_slug, session=session)

        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        posts = await repository_posts.get_all_posts_by_category_id(category_id=category.id, session=session)

        if len(posts) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Posts not found")

        if redis_client:
            redis_client.set(key, pickle.dumps(posts))
            redis_client.expire(key, 1800)

    else:
        posts = pickle.loads(cached_category_posts)

    return paginate(posts)


@router.put("/{category_id}/update",
            response_model=CategoryResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def update_category(
        updated_category: CategoryChange,
        category_id: int,
        session: db_dependency
) -> models.Category:
    """
    The update_category function is used to update the category.
        The function takes in the id of the category to be updated.

        Args:
            updated_category: CategoryChange: Validate the request body
            category_id: int: Get the id of the category to be updated
            session: db_dependency: Access the database

    Returns:
        The category object
    """
    category = await repository_categories.get_category_by_id(category_id=category_id, session=session)

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    updated_category = await repository_categories.update_category(
        updated_category=updated_category, category_id=category_id, session=session
    )

    await delete_cache_in_redis()

    return updated_category


@router.delete("/{category_id}/delete",
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(allowed_operation_admin_moderator)])
async def delete_category(category_id: int, session: db_dependency) -> None:
    """
    The delete_category function is used to delete the category.
        The function takes in the id of the category to be unarchived.

        Args:
            category_id: int: Get the id of the category to be unarchived
            session: db_dependency: Access the database

    Returns:
        None
    """
    category = await repository_categories.get_category_by_id(category_id=category_id, session=session)

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    await repository_categories.delete_category(category_id=category_id, session=session)

    await delete_cache_in_redis()
