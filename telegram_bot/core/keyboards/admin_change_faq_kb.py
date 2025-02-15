from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


admin_change_faq_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Редактирование тем',
            callback_data='change_topics'
        )
    ],
[
        InlineKeyboardButton(
            text='Добавление тем',
            callback_data='add_topics'
        )
    ],
    [
        InlineKeyboardButton(
            text='Редактирование вопросов и ответов',
            callback_data='change_questions_and_answers'
        )
    ],
    [
        InlineKeyboardButton(
            text='Добавление вопросов и ответов',
            callback_data='add_questions_and_answers'
        )
    ],
    [
        InlineKeyboardButton(
            text='Удаление документов к ответам',
            callback_data='delete_answer_documents'
        )
    ],
    [
        InlineKeyboardButton(
            text='Добавление документов к ответам',
            callback_data='add_answer_documents'
        )
    ]
])

admin_actions_topics_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Изменить тему',
            callback_data='change_topic'
        )
    ],
    [
        InlineKeyboardButton(
            text='Удалить тему',
            callback_data='delete_topic'
        )
    ]
])

admin_actions_questions_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Изменить вопрос',
            callback_data='change_question'
        )
    ],
    [
        InlineKeyboardButton(
            text='Изменить ответ',
            callback_data='change_answer'
        )
    ],
    [
        InlineKeyboardButton(
            text='Изменить вопрос и ответ',
            callback_data='change_both'
        )
    ],
    [
        InlineKeyboardButton(
            text='Удалить вопрос',
            callback_data='delete_question'
        )
    ]
])


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
                text=question_dict[1],
                callback_data=f"doc_qa_id_{question_dict[0]}",
            )
        ] for question_dict in current_page_questions
    ]

    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(
            InlineKeyboardButton(
                text='<< Назад',
                callback_data=f'qa_doc_page_{page - 1}'
            )
        )

    # Add the "Cancel" button in the middle
    pagination_buttons.append(
        InlineKeyboardButton(
            text='Отмена',
            callback_data='qa_doc_cancel_action'
        )
    )

    if page < total_pages:
        pagination_buttons.append(
            InlineKeyboardButton(
                text='Вперед >>',
                callback_data=f'qa_doc_page_{page + 1}'
            )
        )

    if pagination_buttons:
        keyboard.append(pagination_buttons)

    keyboard_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return keyboard_markup


async def create_paginated_keyboard_docs(qa_id, list_doc_id, list_doc_name, page=1, items_per_page=10):
    # Calculate the total number of pages
    list_docs = list(zip(list_doc_id, list_doc_name))
    total_pages = (len(list_docs) + items_per_page - 1) // items_per_page

    # Get the questions for the current page
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    current_page_questions = list_docs[start_index:end_index]

    # Create the keyboard buttons for the current page questions
    keyboard = [
        [
            InlineKeyboardButton(
                text=doc[1],
                callback_data=f"doc_id_{doc[0]}",
            )
        ] for doc in list_docs
    ]

    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(
            InlineKeyboardButton(
                text='<< Назад',
                callback_data=f'doc_page_{qa_id}_{page - 1}'
            )
        )

    # Add the "Cancel" button in the middle
    pagination_buttons.append(
        InlineKeyboardButton(
            text='Отмена',
            callback_data='doc_cancel_action'
        )
    )

    if page < total_pages:
        pagination_buttons.append(
            InlineKeyboardButton(
                text='Вперед >>',
                callback_data=f'doc_page_{qa_id}_{page + 1}'
            )
        )

    if pagination_buttons:
        keyboard.append(pagination_buttons)

    keyboard_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return keyboard_markup
