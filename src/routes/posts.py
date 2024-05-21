from fastapi import APIRouter, status, Depends, HTTPException, UploadFile
from fastapi_pagination import Page, paginate

from src.core.database import models
from src.core.database.db_settings.db_helper import db_dependency

from src.schemas.posts import PostResponse, PostCreate, PostPartialUpdate, PostMessageResponse

from src.repositories import categories as repository_categories
from src.repositories import posts as repository_posts

from src.services.auth import auth_service
from src.services.validation import validate_image

router = APIRouter(tags=["Posts"])


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    category_id: int,
    session: db_dependency,
    current_author: models.Author = Depends(auth_service.get_current_author),
) -> models.Post:
    category = await repository_categories.get_category_by_id(session=session, category_id=category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    new_post = await repository_posts.create_post(
        session=session, post_data=post_data, author_id=current_author.id, category_id=category.id
    )

    return new_post


@router.get("/", response_model=Page[PostResponse])
async def get_all_posts(session: db_dependency) -> list[models.Post]:

    posts = await repository_posts.get_all_posts(session=session)

    if len(posts) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Posts not found")

    return paginate(posts)


@router.get("/{post_id}", response_model=PostResponse)
async def get_single_post(session: db_dependency, post_id: int) -> models.Post:
    post = await repository_posts.get_specific_post_by_id(session=session, post_id=post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    return post


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    session: db_dependency,
    post_update: PostPartialUpdate,
    post_id: int,
    current_author: models.Author = Depends(auth_service.get_current_author),
) -> models.Post:
    post = await repository_posts.get_specific_post_by_id(post_id=post_id, session=session)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    updated_post = await repository_posts.partial_update_post(
        session=session, post_id=post_id, post_update=post_update, author_id=current_author.id
    )

    return updated_post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    session: db_dependency,
    post_id: int,
    current_author: models.Author = Depends(auth_service.get_current_author),
) -> None:
    post = await repository_posts.get_specific_post_by_id(post_id=post_id, session=session)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    await repository_posts.delete_post(session=session, post_id=post_id, author_id=current_author.id)


@router.post("/{post_id}/upload-image", response_model=PostMessageResponse)
async def upload_post_image(
    post_id: int,
    session: db_dependency,
    file: UploadFile = Depends(validate_image),
    current_author: models.Author = Depends(auth_service.get_current_author),
) -> dict[str, str]:
    post = await repository_posts.get_post_by_id_and_by_author_id(
        post_id=post_id, author_id=current_author.id, session=session
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found",
        )

    await repository_posts.upload_post_image(file=file, post=post, session=session)

    return {"message": "Post Image uploaded successfully"}
