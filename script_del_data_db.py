import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoSuchTableError

from src.core.database.db_settings.db_helper import get_async_session
from src.core.database.models import Author

logger = logging.getLogger(__name__)


async def get_table_names(models: list) -> list:
    table_names = []
    for model in models:
        table_names.append(model.__table__.name)
    return table_names


async def clear_tables(table_names: list, session: AsyncSession) -> None:
    async with session.begin():
        for table_name in table_names:
            try:
                select_stmt = select(1).select_from(text(table_name)).limit(1)
                await session.execute(select_stmt)
            except NoSuchTableError:
                print(f"Table {table_name} does not exist.")
                logger.error(f"Table {table_name} does not exist.")
                continue

            delete_stmt = text(f"DELETE FROM {table_name}")
            await session.execute(delete_stmt)
            await session.commit()
            print(f"Table {table_name} successfully cleared.")
            logger.info(f"Table {table_name} successfully cleared.")


async def main() -> None:
    model_classes = [Author]
    table_names_to_clear = await get_table_names(model_classes)

    session_gen = get_async_session()
    session = await session_gen.__anext__()

    async with session:
        await clear_tables(table_names_to_clear, session)


if __name__ == "__main__":
    asyncio.run(main())
