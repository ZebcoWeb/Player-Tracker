from mongoengine import connect

from modules.config import Env
from modules.utils import get_logger, LogType



connect(
        Env.DATABASE_DB, 
        host=Env.DATABASE_HOST,
        port=27017
    )