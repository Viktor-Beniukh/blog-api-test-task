from fastapi import APIRouter, Depends, HTTPException, status

from src.core.database import models
from src.core.database.db_settings.db_helper import db_dependency
from src.core.database.models.enums import Role

from src.schemas.tags import TagResponse, TagUpdate
from src.repositories import tags as repository_tags
from src.services.roles import RoleAccess

router = APIRouter(tags=["Tags"])

allowed_operation_admin_moderator = RoleAccess([Role["admin"], Role["moderator"]])


@router.put("/{tag_id}",
            response_model=TagResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)],)
async def update_tag(session: db_dependency, tag_update: TagUpdate, tag_id: int) -> models.Tag:
    """
    The update_post function updates a post data in the database.
    It takes a TagUpdate object as input, and returns the newly updated tag data.

        Args:
            tag_update: TagUpdate: Receive the data of the tag to be updated
            tag_id: int: Get the id of the tag to be updated its data
            session: AsyncSession: Access the database

    Returns:
        The updated tag data
    """
    tag = await repository_tags.get_tag_by_id(session=session, tag_id=tag_id)

    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    updated_tag = await repository_tags.update_tag(session=session, tag_id=tag.id, tag_update=tag_update)

    return updated_tag


@router.delete("/{tag_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(allowed_operation_admin_moderator)],)
async def delete_tag(session: db_dependency, tag_id: int) -> None:
    """
    The delete_tag function is used to delete the tag.
        The function takes in the id of the tag to be deleted.

        Args:
            tag_id: int: Get the id of the tag to be deleted
            session: db_dependency: Access the database

    Returns:
        None
    """
    await repository_tags.delete_tag(session=session, tag_id=tag_id)
