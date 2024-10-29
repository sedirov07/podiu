import logging
from logging_config import conf_logging
from datetime import datetime
from core.data_bases.data_base import PodiuDatabase
from core.utils.change_dir import delete_dir


conf_logging()


class ApplicationsTable(PodiuDatabase):
    async def add_application(self, data):
        insert_query = """
                    INSERT INTO submitted_applications (
                        telegram_id, last_name, first_name, country, date_of_birth,
                        contact_phone, email, previous_education_country, passport_file, passport_text,
                        passport_translation_file, passport_translation_text, visa_application_form_file,
                        visa_application_form_text, bank_statement_file, bank_statement_text,
                        application_for_self, comments, status
                    )
                    VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19
                    )
                """
        if 'user_id' in data:
            del data['user_id']

        try:
            # Преобразование даты
            data['date_of_birth'] = datetime.strptime(data['date_of_birth'], '%m-%d-%Y').strftime('%Y-%m-%d')

            # Преобразование значения application_for_self
            data['application_for_self'] = 1 if data['application_for_self'] else 0

            # Получение значений в правильном порядке
            values = (
                data['telegram_id'], data['last_name'], data['first_name'], data['country'], data['date_of_birth'],
                data['contact_phone'], data['email'], data['previous_education_country'], data['passport'],
                data['passport_text'], data['ru_passport'], data['ru_passport_text'],
                data['visa'], data['visa_text'], data['bank_statement'], data['bank_statement_text'],
                data['application_for_self'], data['comments'], data['status']
            )

            # Выполнение запроса
            await self.execute_query(insert_query, *values)
            return True

        except Exception as e:
            logging.error(f'Error while inserting application data in db: {e}')
            logging.error(f'Values: {values}')
            logging.exception("Exception details:")

            return False

    async def get_application(self, telegram_id):
        select_query = """
            SELECT * FROM submitted_applications WHERE telegram_id = $1
        """
        row = await self.execute_query(select_query, telegram_id, record_class=dict)
        pdf = {}
        jpg = {}
        text = {}
        if row is not None:
            for key, value in row[0].items():
                if key == 'application_for_self':
                    text['application for self'] = 'For myself' if value else 'For another person'
                elif not value:
                    text[key] = ' '
                elif isinstance(value, int):
                    text[key.replace('_', ' ')] = value
                elif 'date' in key:
                    text['date of birth'] = value.strftime("%d-%m-%Y")
                elif 'pdf' in value:
                    pdf[key.replace('_', ' ')] = value
                elif 'jpg' in value:
                    jpg[key.replace('_', ' ')] = value
                else:
                    text[key.replace('_', ' ')] = value
            return text, pdf, jpg
        else:
            return None, None, None

    async def get_applications_awaiting_review(self):
        select_query = """
            SELECT * FROM submitted_applications WHERE status = 'awaiting review'
        """
        rows = await self.execute_query(select_query, record_class=dict)

        # Получение имен столбцов
        columns = [column[0] for column in rows[0].items()]

        # Создание списка словарей
        modified_rows = [dict(zip(columns, row.values())) for row in rows]
        return modified_rows

    async def update_status(self, telegram_id, text):
        update_query = """
            UPDATE submitted_applications SET status = $1 WHERE telegram_id = $2
        """
        await self.execute_query(update_query, text, telegram_id)

    async def delete_application(self, telegram_id):
        await delete_dir(telegram_id)
        delete_query = """
            DELETE FROM submitted_applications WHERE telegram_id = $1
        """
        await self.execute_query(delete_query, telegram_id)

    async def update_columns_by_dict(self, data, telegram_id):
        date_object = datetime.strptime(data['date of birth'], "%d-%m-%Y")
        data['date of birth'] = date_object.strftime("%Y-%m-%d")
        data['application for self'] = 1 if data['application for self'] == 'For myself' else 0

        set_clause = ", ".join([f"{key.replace(' ', '_')} = ${i + 1}" for i, (key, value) in enumerate(data.items())])

        update_query = f"""
                UPDATE submitted_applications SET {set_clause} WHERE telegram_id = ${len(data) + 1}
            """

        values = list(data.values()) + [telegram_id]

        await self.execute_query(update_query, *values)

    async def get_user_language(self, user_id):
        select_query = 'SELECT user_lang FROM users_lang WHERE user_id = $1'
        try:
            lang = await self.execute_query(select_query, user_id)
            if lang:
                return lang[0]
            else:
                return 'en'
        except Exception as e:
            logging.error(f'Error in get_user_language: {e}')
            return 'en'
