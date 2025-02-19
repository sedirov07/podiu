import re


# async def fix_unclosed_markdown_tags(text: str) -> str:
#     """
#     Исправляет незакрытые Markdown-теги, добавляя недостающие закрывающие символы.
#     Поддерживаемые теги: **, *, `, ~~
#     """
#     tags = [r'\*\*', r'\*', r'`', r'~~']  # Поддерживаемые теги
#
#     for tag in tags:
#         count = len(re.findall(tag, text))
#         if count % 2 != 0:
#             text += tag  # Добавляем закрывающий тег в конец строки
#
#     return text
#
#
# async def split_text_with_markdown(text: str, max_length: int):
#     """
#     Разбивает текст на части, сохраняя целостность Markdown-тегов.
#     """
#     parts = []
#     while len(text) > max_length:
#         split_index = text.rfind(' ', 0, max_length)
#         if split_index == -1:
#             split_index = max_length
#         parts.append(await fix_unclosed_markdown_tags(text[:split_index]))
#         text = text[split_index:].lstrip()
#     parts.append(await fix_unclosed_markdown_tags(text))
#     return parts

async def split_text_with_markdown(text, max_length):
    if len(text) <= max_length:
        return [text,]

    parts = []
    current_part = ""
    stack = []  # Стек для отслеживания открытых тегов

    # Регулярное выражение для поиска тегов Markdown
    markdown_tags = re.compile(r'(\[.*?\]\(.*?\)|[*_]{1,2}.*?[*_]{1,2})')

    # Разделяем текст по строкам
    lines = text.split('\n')

    for line in lines:
        # Если добавление текущей строки не превышает максимальную длину
        if len(current_part) + len(line) + 1 <= max_length:
            current_part += line + '\n'
        else:
            # Если превышает, добавляем текущую часть в parts и начинаем новую
            parts.append(current_part.strip())
            current_part = line + '\n'

        # Проверяем и обновляем стек тегов
        for tag in markdown_tags.findall(line):
            if tag.startswith(('*', '_')):
                if stack and stack[-1] == tag:
                    stack.pop()
                else:
                    stack.append(tag)

    # Добавляем последнюю часть
    if current_part:
        parts.append(current_part.strip())

    # Закрываем все открытые теги в последней части
    if stack:
        last_part = parts[-1]
        for tag in reversed(stack):
            if tag.startswith('*'):
                last_part += '*'
            elif tag.startswith('_'):
                last_part += '_'
        parts[-1] = last_part

    return parts
