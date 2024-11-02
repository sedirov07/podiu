from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def create_paginated_keyboard(questions_list, page=1, items_per_page=10):
    # Calculate the total number of pages
    total_pages = (len(questions_list) + items_per_page - 1) // items_per_page

    # Get the questions for the current page
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    current_page_questions = questions_list[start_index:end_index]

    # Create the keyboard buttons for the current page questions
    keyboard = [
        [
            InlineKeyboardButton(
                text=question_dict['question'],
                callback_data=f"q_id_{question_dict['id']}",
            )
        ] for question_dict in current_page_questions
    ]

    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(
            InlineKeyboardButton(
                text='<< Назад',
                callback_data=f'page_{page - 1}'
            )
        )

    # Add the "Cancel" button in the middle
    pagination_buttons.append(
        InlineKeyboardButton(
            text='Отмена',
            callback_data='cancel_action'
        )
    )

    if page < total_pages:
        pagination_buttons.append(
            InlineKeyboardButton(
                text='Вперед >>',
                callback_data=f'page_{page + 1}'
            )
        )

    if pagination_buttons:
        keyboard.append(pagination_buttons)

    keyboard_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return keyboard_markup


questions_actions_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Посмотреть ответ',
            callback_data='get_answer_api'
        )
    ],
[
        InlineKeyboardButton(
            text='Изменить вопрос',
            callback_data='change_question_api'
        )
    ],
    [
        InlineKeyboardButton(
            text='Удалить вопрос',
            callback_data='delete_question_api'
        )
    ]
])
