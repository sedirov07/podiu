import asyncpg
import logging
from logging_config import conf_logging


conf_logging()


class PodiuDatabase:
    def __init__(self, connector: asyncpg.pool.Pool):
        self.connector = connector

    async def execute_query(self, query, *args, record_class=None):
        query = query.strip()
        async with self.connector.acquire() as connection:
            if 'SELECT' in query:
                result = await connection.fetch(query, *args)
                if record_class is not None:
                    results = [record_class(**record) for record in result]
                    return results
                else:
                    results = [dict(record) for record in result]
                    return results
            else:
                await connection.execute(query, *args)
