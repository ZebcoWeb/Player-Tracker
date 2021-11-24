from os import getenv

from dotenv import load_dotenv



class Env:
    load_dotenv('data/.env')

    TOKEN = str(getenv('TOKEN'))
    TODOIST_TOKEN = str(getenv('TODOIST_TOKEN'))
    
    DATABASE_HOST = str(getenv('DATABASE_HOST'))
    DATABASE_DB = str(getenv('DATABASE_DB'))
    DATABASE_USER = str(getenv('DATABASE_USER'))
    DATABASE_PASSWORD = str(getenv('DATABASE_PASSWORD'))


    CACHE_HOST = str(getenv('CACHE_HOST'))
    CACHE_USER = str(getenv('CACHE_USER'))
    CACHE_PASSWORD = str(getenv('CACHE_PASSWORD'))
