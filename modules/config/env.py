from os import getenv

from dotenv import load_dotenv



class Env:
    load_dotenv('data/.env')

    TOKEN = str(getenv('TOKEN'))

    DATABASE_HOST = str(getenv('DATABASE_HOST'))
    DATABASE_DB = str(getenv('DATABASE_DB'))
    DATABASE_USER = str(getenv('DATABASE_USER'))
    DATABASE_PASSWORD = str(getenv('DATABASE_PASSWORD'))
