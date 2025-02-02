import os
from decouple import config


def get_config(name):
    return config(name, default=os.getenv(name))


def setup_environment():
#     os.environ["DB_USER"] = get_config("DB_USER")
#     os.environ["DB_PASSWORD"] = get_config("DB_PASSWORD")
#     os.environ["DB_HOST"] = get_config("DB_HOST")
#     os.environ["DB_PORT"] = get_config("DB_PORT")
#     os.environ["DB_NAME"] = get_config("DB_NAME")
    os.environ["API_HOST"] = get_config("API_HOST")
    os.environ["API_PORT"] = get_config("API_PORT")
    os.environ["AUTH_KEY"] = get_config("AUTH_KEY")
    os.environ["MODEL_NAME"] = get_config("MODEL_NAME")
    os.environ["SCOPE"] = get_config("SCOPE")
