import asyncpg
import logging
from logging_config import conf_logging
from core.data_bases.data_base import PodiuDatabase


conf_logging()


class AdminsTable(PodiuDatabase):
    async def add_admin(self, user_id, user_name):
        try:
            insert_query = "INSERT INTO admins (user_id, user_name) VALUES ($1, $2)"
            result = await self.execute_query(insert_query, user_id, user_name)
            return result
        except Exception as e:
            logging.error(f"Error adding admin: {e}")
            raise

    async def delete_admin(self, user_id):
        try:
            delete_query = "DELETE FROM admins WHERE user_id = $1"
            result = await self.execute_query(delete_query, user_id)
            return result
        except Exception as e:
            logging.error(f"Error deleting admin: {e}")
            raise

    async def get_admins_id(self):
        try:
            select_query = "SELECT user_id FROM admins"
            result = await self.execute_query(select_query)
            return [admin[0] for admin in result]
        except Exception as e:
            logging.error(f"Error getting admins IDs: {e}")
            raise

    async def get_admins_name(self):
        try:
            select_query = "SELECT user_name FROM admins"
            result = await self.execute_query(select_query)
            return [admin[0] for admin in result]
        except Exception as e:
            logging.error(f"Error getting admins names: {e}")
            raise

    async def get_full_admins_info(self):
        try:
            select_query = "SELECT user_id, user_name FROM admins"
            result = await self.execute_query(select_query, record_class=dict)
            return result
        except Exception as e:
            logging.error(f"Error getting full admins info: {e}")
            raise
