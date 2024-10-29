import logging
from core.data_bases.data_base import PodiuDatabase
from logging_config import conf_logging


conf_logging()


class LanguagesTable(PodiuDatabase):
    async def add_user(self, user_id, user_lang):
        insert_query = '''
        INSERT INTO users_lang (user_id, user_lang) VALUES ($1, $2)
        ON CONFLICT (user_id) DO UPDATE SET user_lang = EXCLUDED.user_lang
        '''
        try:
            await self.execute_query(insert_query, user_id, user_lang)
        except Exception as e:
            logging.error(f'Error in add_user: {e}')

    async def get_user_language(self, user_id):
        select_query = 'SELECT user_lang FROM users_lang WHERE user_id = $1'
        try:
            lang = await self.execute_query(select_query, user_id)
            if lang:
                return lang[0]
            else:
                return None
        except Exception as e:
            logging.error(f'Error in get_user_language: {e}')
            return None

    async def get_users_languages(self):
        select_query = 'SELECT user_id, user_lang FROM users_lang'
        try:
            user_lang_pairs = await self.execute_query(select_query, record_class=dict)
            users_languages = {pair['user_id']: pair['user_lang'] for pair in user_lang_pairs}
            return users_languages
        except Exception as e:
            logging.error(f'Error in get_users_languages: {e}')
            return {}
