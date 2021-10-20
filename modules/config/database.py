from mongoengine import connect

from modules.config import Env
from modules.utils import get_logger, LogType


try:

    connect(
        Env.DATABASE_DB, 
        host=Env.DATABASE_HOST, 
        port=27017
    )
    
except Exception as e:

    get_logger(LogType.Database).critical('Database not connected: ' + e)