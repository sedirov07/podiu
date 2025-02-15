import hashlib


async def hash_string(input_string):
    # Создаем объект хэша
    sha1 = hashlib.sha1()

    # Обновляем хэш с байтами исходной строки
    sha1.update(input_string.encode())

    # Получаем хеш в виде шестнадцатеричной строки
    hashed_string = sha1.hexdigest()

    return hashed_string


async def find_question_by_hash(faq_dict, topic, hash_to_find):
    for question, answer_date in faq_dict[topic].items():
        calculated_hash = hashlib.sha1(question.encode()).hexdigest()
        if calculated_hash == hash_to_find:
            return question
