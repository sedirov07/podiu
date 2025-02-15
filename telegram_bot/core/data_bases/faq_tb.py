import logging
from core.data_bases.data_base import PodiuDatabase
from logging_config import conf_logging


conf_logging()


class FAQTable(PodiuDatabase):
    async def get_faq_dict(self):
        query = '''
        SELECT t.topic_name, qa.question, qa.answer, qf.file_name, qf.file_path
        FROM topics t
        LEFT JOIN questions_answers qa ON t.topic_id = qa.topic_id
        LEFT JOIN questions_files qf on qf.qa_id = qa.qa_id
        '''
        faq_dict = {}
        try:
            faq_data = await self.execute_query(query, record_class=dict)
            for row in faq_data:
                topic_name, question, answer, file_name, file_path = (
                    row['topic_name'], row['question'], row['answer'], row['file_name'], row['file_path']
                )

                if topic_name not in faq_dict:
                    faq_dict[topic_name] = {}
                if question:
                    if question not in faq_dict[topic_name]:
                        faq_dict[topic_name][question] = {'answer': answer, 'file_names': [file_name,],
                                                          'file_paths': [file_path,]}
                    else:
                        # Добавляем файлы в список
                        faq_dict[topic_name][question]['file_names'].append(file_name)
                        faq_dict[topic_name][question]['file_paths'].append(file_path)

        except Exception as e:
            logging.error(f'Error in get_faq_dict: {e}')

        return faq_dict

    async def get_questions_and_paths(self):
        query = '''
        SELECT qa.qa_id, qa.question, qf.file_id, qf.file_name, qf.file_path
        FROM questions_answers qa
        LEFT JOIN questions_files qf on qf.qa_id = qa.qa_id
        '''
        questions_and_paths = []
        try:
            faq_data = await self.execute_query(query, record_class=dict)
            qa_id_old = None
            for row in faq_data:
                qa_id, question, file_id, file_name, file_path = (
                    row['qa_id'], row['question'], row['file_id'], row['file_name'], row['file_path']
                )

                if qa_id != qa_id_old:
                    questions_and_paths.append([qa_id, question, [file_id,], [file_name,], [file_path,]])
                else:
                    qap = questions_and_paths.pop()
                    qap[-3].append(file_id)
                    qap[-2].append(file_name)
                    qap[-1].append(file_path)
                    questions_and_paths.append(qap)

                qa_id_old = qa_id
        except Exception as e:
            logging.error(f'Error in get_questions_and_paths: {e}')

        return questions_and_paths

    async def add_topic(self, topic_name):
        check_query = 'SELECT topic_id FROM topics WHERE topic_name = $1'
        insert_query = ("""INSERT INTO topics (topic_id, topic_name)
                        VALUES ((select COALESCE(MAX(topic_id), 0) + 1 FROM topics), $1)""")

        try:
            existing_topic = await self.execute_query(check_query, topic_name)

            if existing_topic:
                return

            await self.execute_query(insert_query, topic_name)

        except Exception as e:
            logging.error(f'Error in add_topic: {e}')

    async def add_question_answer(self, topic_name, question, answer):
        try:
            await self.add_topic(topic_name)

            topic_id_query = 'SELECT topic_id FROM topics WHERE topic_name = $1'

            topic_id = await self.execute_query(topic_id_query, topic_name)

            if topic_id is None:
                raise ValueError("Topic not found")

            topic_id = topic_id[0]
            insert_query = """INSERT INTO questions_answers (qa_id, topic_id, question, answer)
                              VALUES ((select COALESCE(MAX(qa_id), 0) + 1 FROM questions_answers), $1, $2, $3)"""
            await self.execute_query(insert_query, topic_id, question, answer)

        except Exception as e:
            logging.error(f'Error in add_question_answer: {e}')

    async def change_topic(self, old_topic_name, new_topic_name):
        update_query = 'UPDATE topics SET topic_name = $1 WHERE topic_name = $2'
        try:
            await self.execute_query(update_query, new_topic_name, old_topic_name)
        except Exception as e:
            logging.error(f'Error in change_topic: {e}')

    async def change_question(self, topic_name, old_question, new_question, new_answer):
        topic_id_query = 'SELECT topic_id FROM topics WHERE topic_name = $1'
        update_query = ('UPDATE questions_answers SET question = $1, answer = $2'
                        'WHERE topic_id = $3 AND question = $4')
        try:
            topic_id = await self.execute_query(topic_id_query, topic_name)

            if topic_id is None:
                raise ValueError("Topic not found")

            topic_id = topic_id[0]

            await self.execute_query(update_query, new_question, new_answer, topic_id, old_question)

        except Exception as e:
            logging.error(f'Error in change_question: {e}')

    async def delete_question(self, question):
        select_query = 'SELECT qa_id FROM questions_answers WHERE question = $1'
        delete_query = 'DELETE FROM questions_answers WHERE question = $1'
        try:
            result = await self.execute_query(select_query, question)

            if result:
                await self.execute_query(delete_query, question)

        except Exception as e:
            logging.error(f'Error in delete_question: {e}')

    async def delete_topic(self, topic_name):
        topic_id_query = 'SELECT topic_id FROM topics WHERE topic_name = $1'
        question_count_query = 'SELECT COUNT(*) FROM questions_answers WHERE topic_id = $1'
        delete_topic_query = 'DELETE FROM topics WHERE topic_id = $1'

        try:
            topic_id = await self.execute_query(topic_id_query, topic_name)

            if topic_id:
                topic_id = topic_id[0]
                question_count = await self.execute_query(question_count_query, topic_id)
                if question_count[0] == 0:
                    await self.execute_query(delete_topic_query, topic_id)
                    return True

        except Exception as e:
            logging.error(f'Error in delete_topic: {e}')

        return False

    async def delete_document(self, doc_id):
        delete_document_query = 'DELETE FROM questions_files WHERE file_id = $1'

        try:
            await self.execute_query(delete_document_query, doc_id)
        except Exception as e:
            logging.error(f'Error in delete_document: {e}')

    async def add_document(self, question, file_name, file_path):
        try:
            select_query = 'SELECT qa_id from questions_answers where question = $1'
            result = await self.execute_query(select_query, question)
            if result:
                qa_id = result[0]
                insert_query = """INSERT INTO questions_files (qa_id, file_name, file_path)
                                  VALUES ($1, $2, $3)"""
                await self.execute_query(insert_query, qa_id, file_name, file_path)
            else:
                logging.error(f'No question like {question}')
        except Exception as e:
            logging.error(f'Error in add_document: {e}')