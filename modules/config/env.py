from os import getenv

from dotenv import load_dotenv



class Env:
    load_dotenv('data/.env')

    TOKEN = str(getenv('TOKEN'))
    TWITTER_BEARER_TOKEN = str(getenv('TWITTER_BEARER_TOKEN'))

    DATABASE_HOST = str(getenv('DATABASE_HOST'))
    DATABASE_DB = str(getenv('DATABASE_DB'))
    DATABASE_USER = str(getenv('MONGO_INITDB_ROOT_USERNAME'))
    DATABASE_PASSWORD = str(getenv('MONGO_INITDB_ROOT_PASSWORD'))

    CACHE_HOST = str(getenv('CACHE_HOST'))
    CACHE_AUTH = str(getenv('CACHE_AUTH'))
