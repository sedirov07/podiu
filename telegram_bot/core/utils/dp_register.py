import os
import asyncpg
from core.utils.states_change_lang import StepsChangeLang
from core.utils.states_choose_faq import StepsChooseFaq
from core.utils.states_change_topic import StepsChangeTopic, StepsAddTopic
from core.utils.states_change_question import StepsChangeQuestion, StepsAddQuestion
from core.utils.states_change_documents import StepsAddDocument
from core.utils.states_approve_app import StepsApproveApp
from core.utils.states_submit_apply import StepsApply
from core.utils.states_mailing import StepsMailing
from core.utils.states_modify_app import StepsModifyApp
from core.utils.states_add_admin import StepsAddAdmin
from core.utils.states_add_operator import StepsAddOperator
from core.utils.states_question_model import StepsQuestionModel
from core.filters.isAdmin import IsAdmin
from core.filters.isOperator import IsOperator
from core.middlewares.language_middleware import LanguageMiddleware
from core.middlewares.faq_middleware import FAQMiddleware
from core.middlewares.admins_middleware import AdminsMiddleware
from core.middlewares.applications_middleware import ApplicationsMiddleware
from core.data_bases.languages_tb import LanguagesTable
from core.data_bases.faq_tb import FAQTable
from core.data_bases.admins_tb import AdminsTable
from core.data_bases.applications_tb import ApplicationsTable
from core.middlewares.db_middleware import DbSession
from functools import partial
from aiogram import F
from aiogram.filters import Command
from core.handlers import (basic, apply, admin_change_faq, admin_modify_admin_list, admin_apply_review, mailing,
                           admin_modify_operators, operator_start, admin_api)


# Получение переменных окружения
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_NAME = os.environ["DB_NAME"]


async def create_pool():
    # print(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
    return await asyncpg.create_pool(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)


async def dp_register(dp):
    pool_connect = await create_pool()
    dp.update.middleware.register(DbSession(pool_connect))
    admins_table = AdminsTable(pool_connect)
    admins_info = await admins_table.get_full_admins_info()
    applications_table = ApplicationsTable(pool_connect)
    admins_id = [admin.get('user_id') for admin in admins_info]

    for admin_id in admins_id:
        await IsAdmin.add_admin(admin_id)

    is_admin = IsAdmin()
    is_operator = IsOperator()

    language_middleware = LanguageMiddleware(LanguagesTable(pool_connect))
    faq_middleware = FAQMiddleware(FAQTable(pool_connect))
    await faq_middleware.load_faq_dict()
    admins_middleware = AdminsMiddleware(admins_table)
    applications_middleware = ApplicationsMiddleware(applications_table)
    await applications_middleware.load_applications()

    dp.message.middleware.register(language_middleware)

    dp.message.middleware.register(faq_middleware)
    dp.callback_query.middleware.register(faq_middleware)

    dp.message.middleware.register(admins_middleware)
    dp.callback_query.middleware.register(admins_middleware)

    dp.message.middleware.register(applications_middleware)
    dp.callback_query.middleware.register(applications_middleware)

    dp.message.register(basic.get_cancel, Command('cancel'))

    dp.message.register(admin_change_faq.get_start, Command('start'), is_admin)
    dp.message.register(operator_start.get_start, Command('start'), is_operator)

    dp.message.register(admin_change_faq.change_faq, F.text.lower() == 'редактирование faq', is_admin)
    dp.message.register(admin_change_faq.change_faq, F.text.lower() == 'редактирование faq', is_operator)

    dp.callback_query.register(admin_change_faq.start_add_topic, F.data == 'add_topics', is_admin)
    dp.message.register(partial(admin_change_faq.finish_add_topic, faq_middleware=faq_middleware), is_admin,
                        StepsAddTopic.GET_TOPIC)
    dp.callback_query.register(admin_change_faq.start_add_topic, F.data == 'add_topics', is_operator)
    dp.message.register(partial(admin_change_faq.finish_add_topic, faq_middleware=faq_middleware), is_operator,
                        StepsAddTopic.GET_TOPIC)

    dp.callback_query.register(admin_change_faq.start_change_topic, F.data == 'change_topics', is_admin)
    dp.callback_query.register(admin_change_faq.get_topic_to_change, is_admin, StepsChangeTopic.GET_TOPIC)
    dp.callback_query.register(partial(admin_change_faq.change_topic, faq_middleware=faq_middleware), is_admin,
                               StepsChangeTopic.GET_ACTION)
    dp.message.register(partial(admin_change_faq.rename_topic, faq_middleware=faq_middleware), is_admin,
                        StepsChangeTopic.GET_NEW_TOPIC)
    dp.callback_query.register(admin_change_faq.start_change_topic, F.data == 'change_topics', is_operator)
    dp.callback_query.register(admin_change_faq.get_topic_to_change, is_operator, StepsChangeTopic.GET_TOPIC)
    dp.callback_query.register(partial(admin_change_faq.change_topic, faq_middleware=faq_middleware), is_operator,
                               StepsChangeTopic.GET_ACTION)
    dp.message.register(partial(admin_change_faq.rename_topic, faq_middleware=faq_middleware), is_operator,
                        StepsChangeTopic.GET_NEW_TOPIC)

    dp.callback_query.register(admin_change_faq.start_add_question, F.data == 'add_questions_and_answers', is_admin)
    dp.callback_query.register(admin_change_faq.get_topic_of_question_to_add, is_admin, StepsAddQuestion.GET_TOPIC)
    dp.message.register(admin_change_faq.get_question_to_add, is_admin, StepsAddQuestion.GET_QUESTION)
    dp.message.register(partial(admin_change_faq.finish_add_question, faq_middleware=faq_middleware), is_admin,
                        StepsAddQuestion.GET_ANSWER)
    dp.callback_query.register(admin_change_faq.start_add_question, F.data == 'add_questions_and_answers', is_operator)
    dp.callback_query.register(admin_change_faq.get_topic_of_question_to_add, is_operator, StepsAddQuestion.GET_TOPIC)
    dp.message.register(admin_change_faq.get_question_to_add, is_operator, StepsAddQuestion.GET_QUESTION)
    dp.message.register(partial(admin_change_faq.finish_add_question, faq_middleware=faq_middleware), is_operator,
                        StepsAddQuestion.GET_ANSWER)

    dp.callback_query.register(admin_change_faq.start_change_question, F.data == 'change_questions_and_answers',
                               is_admin)
    dp.callback_query.register(admin_change_faq.get_topic_of_question_to_change, is_admin,
                               StepsChangeQuestion.GET_TOPIC)
    dp.callback_query.register(admin_change_faq.get_question_to_change, is_admin, StepsChangeQuestion.GET_QUESTION)
    dp.callback_query.register(partial(admin_change_faq.change_question, faq_middleware=faq_middleware), is_admin,
                               StepsChangeQuestion.GET_ACTION)
    dp.message.register(partial(admin_change_faq.rename_question, faq_middleware=faq_middleware), is_admin,
                        StepsChangeQuestion.GET_NEW_QUESTION)
    dp.message.register(partial(admin_change_faq.rename_answer, faq_middleware=faq_middleware), is_admin,
                        StepsChangeQuestion.GET_NEW_ANSWER)
    dp.callback_query.register(admin_change_faq.start_change_question, F.data == 'change_questions_and_answers',
                               is_operator)
    dp.callback_query.register(admin_change_faq.get_topic_of_question_to_change, is_operator,
                               StepsChangeQuestion.GET_TOPIC)
    dp.callback_query.register(admin_change_faq.get_question_to_change, is_operator, StepsChangeQuestion.GET_QUESTION)
    dp.callback_query.register(partial(admin_change_faq.change_question, faq_middleware=faq_middleware), is_operator,
                               StepsChangeQuestion.GET_ACTION)
    dp.message.register(partial(admin_change_faq.rename_question, faq_middleware=faq_middleware), is_operator,
                        StepsChangeQuestion.GET_NEW_QUESTION)
    dp.message.register(partial(admin_change_faq.rename_answer, faq_middleware=faq_middleware), is_operator,
                        StepsChangeQuestion.GET_NEW_ANSWER)
    # Удаление документов
    dp.callback_query.register(admin_change_faq.start_delete_document, F.data == 'delete_answer_documents',
                               is_admin)
    dp.callback_query.register(admin_change_faq.choose_document, F.data.startswith('doc_qa_id_'), is_admin)
    dp.callback_query.register(partial(admin_change_faq.delete_document, faq_middleware=faq_middleware),
                               F.data.startswith('doc_id_'), is_admin)

    dp.callback_query.register(admin_change_faq.start_delete_document, F.data == 'delete_answer_documents',
                               is_operator)
    dp.callback_query.register(admin_change_faq.choose_document, F.data.startswith('doc_qa_id_'), is_operator)
    dp.callback_query.register(partial(admin_change_faq.delete_document, faq_middleware=faq_middleware),
                               F.data.startswith('doc_id_'), is_operator)

    # Добавление документов
    dp.callback_query.register(admin_change_faq.start_add_document, F.data == 'add_answer_documents',
                               is_admin)
    dp.callback_query.register(admin_change_faq.get_topic_of_question_to_add_document, is_admin,
                               StepsAddDocument.GET_TOPIC)
    dp.callback_query.register(admin_change_faq.get_question_to_add_document, is_admin, StepsAddDocument.GET_QUESTION)
    dp.message.register(partial(admin_change_faq.get_document_to_add, faq_middleware=faq_middleware),
                        is_admin, StepsAddDocument.GET_DOCUMENT, F.document)

    dp.callback_query.register(admin_change_faq.start_add_document, F.data == 'add_answer_documents',
                               is_operator)
    dp.callback_query.register(admin_change_faq.get_topic_of_question_to_add_document, is_operator,
                               StepsAddDocument.GET_TOPIC)
    dp.callback_query.register(admin_change_faq.get_question_to_add_document, is_operator, StepsAddDocument.GET_QUESTION)
    dp.message.register(partial(admin_change_faq.get_document_to_add, faq_middleware=faq_middleware),
                        is_operator, StepsAddDocument.GET_DOCUMENT, F.document)

    dp.message.register(admin_modify_admin_list.manage, F.text.lower() == 'управление персоналом', is_admin)
    dp.message.register(admin_modify_admin_list.start_delete_admin, F.text.lower() == 'удалить администратора',
                        is_admin)
    dp.callback_query.register(partial(admin_modify_admin_list.finish_delete_admin,
                                       admins_middleware=admins_middleware, is_admin=is_admin),
                               F.data.lower().startswith('delete_admin'), is_admin)

    dp.message.register(admin_modify_admin_list.start_add_admin, F.text.lower() == 'добавить администратора', is_admin)
    dp.message.register(partial(admin_modify_admin_list.finish_add_admin, admins_middleware=admins_middleware,
                                is_admin=is_admin), StepsAddAdmin.GET_ADMIN, is_admin)

    dp.message.register(admin_modify_operators.start_delete_operator, F.text.lower() == 'удалить оператора', is_admin)
    dp.callback_query.register(partial(admin_modify_operators.finish_delete_operator,
                                       admins_middleware=admins_middleware, is_operator=is_operator),
                               F.data.lower().startswith('delete_operator'), is_admin)

    dp.message.register(admin_modify_operators.start_add_operator, F.text.lower() == 'добавить оператора', is_admin)
    dp.message.register(partial(admin_modify_operators.finish_add_operator, admins_middleware=admins_middleware,
                                is_operator=is_operator), StepsAddOperator.GET_OPERATOR, is_admin)
    dp.message.register(partial(admin_modify_operators.get_last_name_operator, admins_middleware=admins_middleware,
                                is_operator=is_operator), StepsAddOperator.GET_LAST_NAME, is_admin)

    dp.message.register(partial(basic.get_start, language_middleware=language_middleware),
                        Command(commands=['start', 'run']))
    dp.message.register(basic.change_lang, F.text.lower() == 'change language')
    dp.message.register(partial(basic.get_lang, language_middleware=language_middleware), StepsChangeLang.GET_LANG)

    dp.message.register(basic.get_topics_faq, F.text.lower().in_(['faq', 'просмотр faq']))
    dp.callback_query.register(basic.get_questions_faq, StepsChooseFaq.GET_TOPIC)
    dp.message.register(basic.get_answer, StepsChooseFaq.NO_ANSWER_IN_FAQ)
    dp.callback_query.register(partial(basic.send_answer_faq, admins_middleware=admins_middleware),
                               StepsChooseFaq.GET_QUESTION or F.data.startswith('contact_with_operator'))

    dp.callback_query.register(partial(basic.operator_ready, admins_middleware=admins_middleware),
                               F.data.startswith('operator_is_ready'), is_operator)
    dp.callback_query.register(basic.operator_not_ready, F.data.startswith('operator_is_not_ready'), is_operator)

    # dp.message.register(partial(apply.start_submit_apply, applications_middleware=applications_middleware),
    #                     F.text.lower() == 'apply')
    # dp.message.register(apply.finish_consent, F.text == "❌ I don't agree", StepsApply.WAITING_FOR_CONSENT)
    # dp.message.register(apply.process_consent, F.text == "✅ I agree", StepsApply.WAITING_FOR_CONSENT)
    # dp.message.register(apply.process_personal_info, StepsApply.WAITING_FOR_PERSONAL_INFO)
    # dp.message.register(apply.process_passport_data, StepsApply.WAITING_FOR_PASSPORT)
    # dp.message.register(apply.process_ru_passport_data, StepsApply.WAITING_FOR_RU_PASSPORT)
    # dp.message.register(apply.process_visa_application_form_data, StepsApply.WAITING_FOR_VISA)
    # dp.message.register(apply.process_bank_statement_data, StepsApply.WAITING_FOR_BANK_STATEMENT)
    # dp.message.register(apply.process_application_type, F.text.in_(["For myself", "For another person"]),
    #                     StepsApply.WAITING_FOR_TYPE)
    # dp.message.register(apply.process_agree_comments, StepsApply.WAITING_FOR_COMMENTS)
    # dp.message.register(partial(apply.finish_apply, applications_middleware=applications_middleware),
    #                     F.text.in_(["✅ Yes", "❌ No"]), StepsApply.WAITING_FOR_APPLY)
    #
    # dp.callback_query.register(partial(admin_apply_review.review_application,
    #                                    applications_middleware=applications_middleware),
    #                            F.data.startswith('review_application'), is_admin)
    # dp.callback_query.register(partial(admin_apply_review.review_application,
    #                                    applications_middleware=applications_middleware),
    #                            F.data.startswith('review_application'), is_operator)
    #
    # dp.message.register(partial(admin_apply_review.approve_application,
    #                             applications_middleware=applications_middleware), is_admin,
    #                     StepsApproveApp.GET_APPROVE)
    # dp.message.register(partial(admin_apply_review.approve_application,
    #                             applications_middleware=applications_middleware), is_operator,
    #                     StepsApproveApp.GET_APPROVE)
    #
    # dp.message.register(admin_apply_review.rejected_application, is_admin, StepsApproveApp.GET_REASON)
    # dp.message.register(admin_apply_review.rejected_application, is_operator, StepsApproveApp.GET_REASON)
    #
    # dp.message.register(admin_apply_review.get_applications_list, is_admin, F.text == 'Список заявлений')
    # dp.message.register(admin_apply_review.get_applications_list, is_operator, F.text == 'Список заявлений')
    #
    # dp.callback_query.register(admin_apply_review.modify_application, F.data.startswith('mod_app_'), is_admin)
    # dp.callback_query.register(admin_apply_review.modify_application, F.data.startswith('mod_app_'), is_operator)
    #
    # dp.message.register(admin_apply_review.update_application, is_admin, StepsModifyApp.GET_NEW_VALUE)
    # dp.message.register(admin_apply_review.update_application, is_operator, StepsModifyApp.GET_NEW_VALUE)
    #
    # dp.message.register(partial(admin_apply_review.process_update_application,
    #                             applications_middleware=applications_middleware), is_admin,
    #                     StepsModifyApp.GET_ANOTHER_NEW_VALUE)
    # dp.message.register(partial(admin_apply_review.process_update_application,
    #                             applications_middleware=applications_middleware), is_operator,
    #                     StepsModifyApp.GET_ANOTHER_NEW_VALUE)

    dp.message.register(mailing.start_mailing, F.text.lower() == 'общая рассылка', is_admin)
    dp.message.register(mailing.get_text_for_mailing, is_admin, StepsMailing.GET_TEXT)
    dp.message.register(partial(mailing.finish_mailing, language_middleware=language_middleware), is_admin,
                        StepsMailing.SEND_MESSAGE)

    dp.message.register(admin_api.change_questions_model, F.text.lower() == 'модель ответов', is_admin)
    dp.callback_query.register(admin_api.get_question_action_model, F.data.startswith('q_id_'), is_admin)
    dp.callback_query.register(admin_api.get_answer_model, F.data == 'get_answer_api', is_admin,
                               StepsQuestionModel.GET_ACTION)

    dp.callback_query.register(admin_api.change_question_model, F.data == 'change_question_api', is_admin,
                               StepsQuestionModel.GET_ACTION)
    dp.message.register(admin_api.get_new_edit_question_model, is_admin, StepsQuestionModel.GET_NEW_QUESTION)
    dp.message.register(admin_api.get_new_edit_answer_model, is_admin, StepsQuestionModel.GET_NEW_ANSWER)

    dp.callback_query.register(admin_api.add_question_model, F.data == 'add_question_api', is_admin)
    dp.message.register(admin_api.add_new_question_model, is_admin, StepsQuestionModel.GET_NEW_QUESTION_ADD)
    dp.message.register(admin_api.add_new_answer_model, is_admin, StepsQuestionModel.GET_NEW_ANSWER_ADD)

    dp.callback_query.register(admin_api.delete_question_model, F.data == 'delete_question_api', is_admin,
                               StepsQuestionModel.GET_ACTION)

    dp.callback_query.register(admin_api.handle_pagination, (F.data.startswith('page_')) | (F.data == 'cancel_action'))
    dp.callback_query.register(admin_change_faq.handle_pagination_faq,
                               (F.data.startswith('qa_doc_page_')) | (F.data == 'qa_doc_cancel_action'))
    dp.callback_query.register(admin_change_faq.handle_pagination_doc,
                               (F.data.startswith('doc_page_')) | (F.data == 'doc_cancel_action'))
