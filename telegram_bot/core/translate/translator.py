import os
import requests
import logging
import re
import aiohttp


YANDEX_API_KEY = os.environ["YANDEX_API_KEY"]
TRANSLATES = {}


async def del_translation_text(text):
    for target_language in TRANSLATES:
        if text in TRANSLATES[target_language]:
            del TRANSLATES[target_language][text]


async def translate_text(text, user_language, target_language, cache=False):
    if cache and user_language == 'en' or user_language == 'ru':
        if target_language in TRANSLATES:
            if text in TRANSLATES[target_language]:
                if TRANSLATES[target_language][text]:
                    return TRANSLATES[target_language][text]
            else:
                TRANSLATES[target_language][text] = ''
        else:
            TRANSLATES[target_language] = {text: ''}

    if user_language == target_language:
        return text

    base_url = 'https://translate.api.cloud.yandex.net/translate/v2/translate'
    params = {
        "sourceLanguageCode": f'{user_language}',  # Язык исходного текста
        "targetLanguageCode": f'{target_language}',  # Язык, на который нужно перевести
        "format": "PLAIN_TEXT",
        "texts": [text],
    }

    headers = {
        'Authorization': f'Api-Key {YANDEX_API_KEY}',
        'Content-Type': 'application/json'
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(base_url, json=params, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    translations = result.get('translations')
                    if translations:
                        for translation in translations:
                            translated_text = translation.get('text')
                            # detected_language = translation.get('detectedLanguageCode')
                            if translated_text and cache:
                                if target_language in TRANSLATES:
                                    TRANSLATES[target_language][text] = translated_text
                                else:
                                    TRANSLATES[target_language] = {text: translated_text}
                            # logging.info(f'{translated_text}')
                            return translated_text
                    else:
                        logging.warning('Translation is not found')
                        return text
                else:
                    logging.warning(f'{response.status}')
                    return text
        except aiohttp.ClientError as e:
            print(f"Error: {e}")
            return text


async def detect_language(text):
    base_url = 'https://translate.api.cloud.yandex.net/translate/v2/detect'
    headers = {
        'Authorization': f'Api-Key {YANDEX_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'text': text
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(base_url, json=data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['languageCode']
                else:
                    logging.warning('Failed to detect language')
                    return 'en'
        except aiohttp.ClientError as e:
            print(f"Error: {e}")
            return text


async def translate_text_with_markdown_links(text, source_language, target_language, cache=False):
    # Перевести весь текст, включая текст гиперссылок
    translated_text = await translate_text(text, source_language, target_language, cache=cache)

    # Регулярное выражение для поиска гиперссылок Markdown
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(link_pattern, text)

    # Для каждой найденной гиперссылки переводим текст ссылки и заменяем в переведенном тексте
    for link_text, url in matches:
        translated_link_text = await translate_text(link_text, source_language, target_language, cache=cache)
        translated_link = f'[{translated_link_text}]({url})'
        # Заменяем все вхождения оригинальной гиперссылки на переведенную
        translated_text = re.sub(
            re.escape(f'[{link_text}]({url})'),
            translated_link,
            translated_text
        )

    # Исправляем незакрытые Markdown-теги
    translated_text = await fix_unclosed_markdown_tags(translated_text)

    return translated_text


async def fix_unclosed_markdown_tags(text: str) -> str:
    """
    Исправляет незакрытые Markdown-теги, добавляя недостающие закрывающие символы.
    Поддерживаемые теги: **, *, `, ~~
    """
    tags = [r'\*', r'\_', r'`', r'~']  # Поддерживаемые теги

    for tag in tags:
        count = len(re.findall(tag, text))
        if count % 2 != 0:
            text += tag.replace('\\', '')  # Добавляем закрывающий тег в конец строки

    return text
