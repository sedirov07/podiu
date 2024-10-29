import os
from decouple import config


def get_config(name):
    return config(name, default=os.getenv(name))


def setup_environment():
    os.environ["OUTLOOK_LOGIN"] = get_config("OUTLOOK_LOGIN")
    os.environ["OUTLOOK_PASSWORD"] = get_config("OUTLOOK_PASSWORD")
    os.environ["API_HOST"] = get_config("API_HOST")
    os.environ["API_PORT"] = get_config("API_PORT")
