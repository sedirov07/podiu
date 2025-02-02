import os
import random
import asyncio
import requests
import markdown
import pytz
from exchangelib import Credentials, Account, Message, DELEGATE, HTMLBody, Configuration
from datetime import datetime, timedelta
from config import setup_environment


# Настройка окружения
setup_environment()

# Получение переменных окружения
OUTLOOK_LOGIN = os.environ["OUTLOOK_LOGIN"]
OUTLOOK_PASSWORD = os.environ["OUTLOOK_PASSWORD"]
API_HOST = os.environ["API_HOST"]
API_PORT = os.environ["API_PORT"]

credentials = Credentials(OUTLOOK_LOGIN, OUTLOOK_PASSWORD)
config = Configuration(server='outlook.office365.com', credentials=credentials)
account = Account(primary_smtp_address=OUTLOOK_LOGIN, config=config, autodiscover=False, access_type=DELEGATE)


# Функция для отправки текста на сервер API и получения ответа
async def send_text_to_api(text):
    api_url = f"http://{API_HOST}:{API_PORT}/get_answer"
    response = requests.post(api_url, json={"question": text})
    if response.status_code == 200:
        text = response.text.replace('"', '').replace(r'\n', '<br>')
        if text:
            return text
    return ''


async def process_incoming_emails():
    while True:
        inbox = account.inbox
        now = datetime.now(pytz.utc)
        ten_minutes_ago = now - timedelta(minutes=10)
        for item in inbox.filter(is_read=False, datetime_received__gt=ten_minutes_ago).order_by('-datetime_received'):
            original_body = item.body

            # Отправка текста на модель, получение ответа и отправка отправителю
            response_text = await send_text_to_api(original_body)

            if len(response_text) == 0:
                item.is_read = True
                item.save()
                continue

            html_text = markdown.markdown(response_text)

            additional_text = "This is an automated response."

            reply_html_body = f'''<font face='Arial' size='3'><p>{original_body}</p><br><br>{additional_text}
                             <br><br><p>{html_text}</p><br><br><p>Sincerely, UrFU POdIU</p></font>'''

            reply = Message(
                account=account,
                folder=account.sent,
                subject=f"Re: {item.subject}",
                body=HTMLBody(reply_html_body),
                to_recipients=[item.sender.email_address]
            )

            reply.send()
            item.is_read = True
            item.save()

        await asyncio.sleep(60 + random.randint(0, 30))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(process_incoming_emails())
