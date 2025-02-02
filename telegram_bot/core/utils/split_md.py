import re


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
