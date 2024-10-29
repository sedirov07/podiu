import asyncpg
from logging_config import conf_logging


conf_logging()


class PodiuDatabase:
    def __init__(self, connector: asyncpg.pool.Pool):
        self.connector = connector

    async def execute_query(self, query, *args, record_class=None):
        query = query.strip()
        for i in range(1, len(args) + 1):
            placeholder = f'${i}'
            if isinstance(args[i-1], str):
                query = query.replace(placeholder, "'" + str(args[i-1]).replace("'", "''") + "'", 1)
            else:
                query = query.replace(placeholder, str(args[i-1]), 1)
        # print(query)
        if 'SELECT' in query:
            result = await self.connector.fetch(query=query)

            if record_class is not None:
                results = [record_class(**record) for record in result]
                return results
            else:
                results = [v for record in result for v in record.values()]
                return results
        else:
            await self.connector.execute(query=query)
