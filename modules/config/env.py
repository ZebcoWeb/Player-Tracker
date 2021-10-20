from os import getenv

from dotenv import load_dotenv, get_key

from modules.utils.enums import LogType
from modules.utils import get_logger



class Env:

    try:
        
        load_dotenv('data/.env')

        LOG_TO_DISCORD = bool(getenv('LOG_TO_DISCORD'))

        DATABASE_HOST = str(getenv('DATABASE_HOST'))
        DATABASE_DB = str(getenv('DATABASE_DB'))
        DATABASE_USER = str(getenv('DATABASE_USER'))
        DATABASE_PASSWORD = str(getenv('DATABASE_PASSWORD'))

        CACHE_HOST = str(getenv('CACHE_HOST'))
        CACHE_USER = str(getenv('CACHE_USER'))
        CACHE_PASSWORD = str(getenv('CACHE_PASSWORD'))

        TOKEN = getenv('TOKEN')

    except Exception as e:
        get_logger(LogType.Env).error(e)