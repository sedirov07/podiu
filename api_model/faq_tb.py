from keybert import KeyBERT
import json
import re
from data_base import PodiuDatabase
from logging_config import conf_logging


conf_logging()
kw_model = KeyBERT()


def get_intersections_count(list1, list2) -> int:
    count = 0
    for word in list1:
        if word in list2:
            count += 1
    return count


def get_keywords(question, kw_model=kw_model, min_score=0.3):
    question = question.lower()
    stop_words = ['ural', 'federal', 'university', 'institute', 'urfu']
    stop_words_pattern = r'\b(?:' + '|'.join(stop_words) + r')\b'
    question = re.sub(stop_words_pattern, '', question)
    question = re.sub(r'\s+', ' ', question).strip()

    keywords = kw_model.extract_keywords(question, keyphrase_ngram_range=(1, 1))
    result = [word[0] for word in keywords if word[1] > min_score]
    if len(result) < 2:
        result = [word[0] for word in keywords if word[1] > min_score*0.7]
    if len(result) < 2:
        result = [word[0] for word in keywords if word[1] > min_score*0.4]
    return result


class FAQTable(PodiuDatabase):
    async def load_questions(self, kw_model=kw_model, text_data=None):
        if text_data is None:
            with open('data2.txt', 'r', encoding="utf-8") as f:
                text_data = f.read()

        lines = text_data.splitlines()
        question = ''
        answer_lines = []

        for line in lines:
            line = line.strip()
            if line.endswith('?'):
                if question:
                    # Вставка предыдущего вопроса-ответа
                    answer = "\n".join(answer_lines).strip()
                    query = """
                        INSERT INTO questions_answers_kw (question, answer, keywords)
                        VALUES ($1, $2, $3)
                    """
                    await self.execute_query(query, question, answer, json.dumps(get_keywords(question, kw_model)))
                    answer_lines = []  # Очистка для нового ответа

                question = line  # Новый вопрос
            else:
                if line:
                    answer_lines.append(line)  # Добавление линии к ответу

        # Вставка последнего вопроса-ответа, если он существует
        if question and answer_lines:
            answer = "\n".join(answer_lines).strip()
            query = """
                INSERT INTO questions_answers_kw (question, answer, keywords)
                VALUES ($1, $2, $3)
            """
            await self.execute_query(query, question, answer, json.dumps(get_keywords(question, kw_model)))

    async def init_insert(self, kw_model=kw_model):
        query = "SELECT COUNT(*) FROM questions_answers_kw"
        count = await self.execute_query(query)
        if count[0]['count'] == 0:
            await self.load_questions(kw_model)

    async def get_answers(self):
        query = "SELECT answer, keywords, question, keywords FROM questions_answers_kw"
        return await self.execute_query(query)

    async def add_answer(self, question):
        query =\
        """
            INSERT INTO questions_answers_kw (question, answer, keywords)
            VALUES ($1, $2, $3)
        """
        await self.execute_query(query, question.question.strip(), question.answer.strip(), json.dumps(get_keywords(question.question, kw_model)))

    async def get_all_answers(self):
        query = "SELECT id, question, answer, keywords FROM questions_answers_kw;"
        results = await self.execute_query(query)
        return [{"id": row["id"], "question": row["question"], "answer": row["answer"], "keywords": row["keywords"]}
                for row in results]

    async def edit_answer(self, question):
        query =\
        """
            UPDATE questions_answers_kw
            SET question = $1, answer = $2, keywords = $3
            WHERE id = $4
        """
        await self.execute_query(query, question.question.strip(), question.answer.strip(), json.dumps(get_keywords(question.question, kw_model)), question.id)

    async def edit_keywords(self, question):
        query =\
        """
            UPDATE questions_answers_kw
            SET keywords = $1
            WHERE id = $2
        """
        await self.execute_query(query, question.keywords, question.id)

    async def delete_answer(self, id):
        query = "DELETE FROM questions_answers_kw WHERE id = $1;"
        await self.execute_query(query, id)
