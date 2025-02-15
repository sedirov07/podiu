import os
from decouple import config


def get_config(name):
    return config(name, default=os.getenv(name))


def setup_environment():
    os.environ["DB_USER"] = get_config("DB_USER")
    os.environ["DB_PASSWORD"] = get_config("DB_PASSWORD")
    os.environ["DB_HOST"] = get_config("DB_HOST")
    os.environ["DB_PORT"] = get_config("DB_PORT")
    os.environ["DB_NAME"] = get_config("DB_NAME")

    os.environ["BOT_TOKEN"] = get_config("BOT_TOKEN")
    os.environ["YANDEX_API_KEY"] = get_config("YANDEX_API_KEY")
    os.environ["FOLDER_ID"] = get_config("FOLDER_ID")
    os.environ["API_OCR"] = get_config("API_OCR")
    os.environ["TG_API_HOST"] = get_config("TG_API_HOST")
    os.environ["TG_API_PORT"] = get_config("TG_API_PORT")
