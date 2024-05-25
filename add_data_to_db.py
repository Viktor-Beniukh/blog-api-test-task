import os
import json
import asyncio
import logging

from fastapi import Path

from sqlalchemy.ext.asyncio import AsyncSession, AsyncConnection
from sqlalchemy import MetaData, Table, Inspector

from create_json_file import create_json_data
from src.services.security import get_password_hash
from src.core.database.db_settings.db_helper import async_session

logger = logging.getLogger(__name__)

create_json_data()

current_dir = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(current_dir, "data.json")


async def load_data_from_json(file_path: Path) -> dict | None:
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        return data
    except Exception as e:
        logger.error(f"Error loading data from JSON: {str(e)}")
        print(f"Error loading data from JSON: {str(e)}")
        return None


async def get_table_metadata(connection: AsyncConnection, table_name: str) -> AsyncConnection:
    def sync_inspect(conn):
        inspector = Inspector.from_engine(conn)
        return Table(table_name, MetaData(), autoload_with=conn)

    return await connection.run_sync(sync_inspect)


async def insert_data_into_tables(data: dict, session: AsyncSession) -> None:
    async with session.begin():
        connection = await session.connection()
        for table_name, items in data.items():
            if table_name == "authors":
                for author in items:
                    author["hashed_password"] = get_password_hash(author["hashed_password"])

            table = await get_table_metadata(connection=connection, table_name=table_name)
            await session.execute(table.insert(), items)
        await session.commit()
        print("Data inserted successfully.")
        logger.info("Data inserted successfully.")


async def main() -> None:
    data_json = await load_data_from_json(file_path=json_file_path)
    if data_json:
        async with async_session() as session:
            await insert_data_into_tables(data=data_json, session=session)
    else:
        print("Failed to load data from JSON.")
        logger.info("Failed to load data from JSON.")


if __name__ == "__main__":
    asyncio.run(main())
