"""Executa migrations e seeders manualmente.

Uso (dentro do container backend):
    python -m scripts.seed
"""

import asyncio
import logging

from app.db.migrations import run_migrations
from app.db.mongodb import close_mongo_connection, connect_to_mongo, get_database
from app.db.seed import run_seeders

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    await connect_to_mongo()
    try:
        database = get_database()
        await run_migrations(database)
        await run_seeders(database)
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())
