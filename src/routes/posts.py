from fastapi import APIRouter, status, Depends, HTTPException, UploadFile
from fastapi_pagination import Page, paginate

from src.core.database import models
from src.core.database.db_settings.db_helper import db_dependency

from src.schemas.posts import (
    PostResponse,
    PostCreate,
    PostPartialUpdate,
    PostMessageResponse,
    PostTagsResponse,
)

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
    """
    The create_post function creates a new post in the database.

        Args:
            post_data: schemas.PostCreate: Validate the request body
            category_id: int: get id of the category to create new post for its
            session: db_dependency: Pass the database session to the repository layer
            current_author (Author): the current author

    Returns:
        A post object
    """
    category = await repository_categories.get_category_by_id(session=session, category_id=category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    new_post = await repository_posts.create_post(
        session=session,
        post_data=post_data,
        author_id=current_author.id,
        category_id=category.id
    )

    return new_post


@router.get("/", response_model=Page[PostTagsResponse])
async def get_all_posts(session: db_dependency) -> list[models.Post]:
    """
    The function returns a list of all posts in the database.

        Args:
            session: db_dependency: Access the database

    Returns:
        A list of posts
    """

    posts = await repository_posts.get_all_posts(session=session)

    if len(posts) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Posts not found")

    return paginate(posts)


@router.get("/{post_slug}", response_model=PostTagsResponse)
async def get_single_post(session: db_dependency, post_slug: str) -> models.Post:
    """
    The function returns a single post in the database.

        Args:
            post_slug: str: Get the slug of the post
            session: db_dependency: Access the database

    Returns:
        A single post
    """
    post = await repository_posts.get_single_post_by_slug(session=session, slug=post_slug)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    return post


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    session: db_dependency,
    post_update: PostPartialUpdate,
    post_id: int,
    current_author: models.Author = Depends(auth_service.get_current_author),
) -> models.Post:
    """
    The update_post function partial updates a post data in the database.
    It takes a PostPartialUpdate object as input, and returns the newly partial updated post data.

        Args:
            post_update: PostPartialUpdate: Receive the data of the post to be updated
            post_id: int: Get the id of the post to be updated its data
            session: AsyncSession: Access the database
            current_author (Author): the current author

    Returns:
        The updated post data
    """
    post = await repository_posts.get_specific_post_by_id(post_id=post_id, session=session)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    updated_post = await repository_posts.partial_update_post(
        session=session, post_id=post.id, post_update=post_update, author_id=current_author.id
    )

    return updated_post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    session: db_dependency,
    post_id: int,
    current_author: models.Author = Depends(auth_service.get_current_author),
) -> None:
    """
    The delete_post function is used to delete the post.
        The function takes in the id of the post to be deleted.

        Args:
            post_id: int: Get the id of the post to be deleted
            session: db_dependency: Access the database
            current_author (Author): the current author

    Returns:
        None
    """
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
    """
    The upload_post_image function uploads post image.

        Args:
            file: UploadFile: upload image
            post_id: int: Get the id of the post to upload image
            session: db_dependency: Access the database
            current_author (Author): the current author

    Returns:
        A message about successful uploading post image
    """
    post = await repository_posts.get_post_by_id_and_by_author_id(
        post_id=post_id, author_id=current_author.id, session=session
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found",
        )

    await repository_posts.upload_post_image(file=file, post=post, session=session)

    return {"message": "Post Image uploaded successfully"}


@router.post("/{post_id}/add_tags", response_model=PostMessageResponse)
async def add_tags_to_post(
    post_id: int,
    tag_names: list[str],
    session: db_dependency,
    current_author: models.Author = Depends(auth_service.get_current_author),
) -> dict[str, str]:
    """
    The add_tags_to_post function creates tag and adds it to association with post.

        Args:
            tag_names: list[str]: Validate the request body
            post_id: int: Get the id of the post to be added it to association with tag
            session: db_dependency: Access the database
            current_author (Author): the current author

    Returns:
        A message about successful adding tag to post
    """

    await repository_posts.add_tags_to_post(
        session=session, post_id=post_id, author_id=current_author.id, tag_names=tag_names
    )

    return {"message": "Tags added to post successfully!"}


@router.delete("/{post_id}/remove_tag", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tag_data_from_post(
    post_id: int,
    tag_id: int,
    session: db_dependency,
    current_author: models.Author = Depends(auth_service.get_current_author),
) -> None:
    """
    The remove_tag_data_from_post function deletes an exists association between post and tag data.

        Args:
            tag_id: int: Validate the request body
            post_id: int: Get the id of the post to be deleted its association with tag
            session: db_dependency: Access the database
            current_author (Author): the current author

    Returns:
        None
    """

    await repository_posts.remove_tag_from_post(
        post_id=post_id, tag_id=tag_id, author_id=current_author.id, session=session
    )
