from rom import util

from modules.config import Env
from modules.utils import LogType, get_logger

try:

    util.set_connection_settings(
        host=Env.CACHE_HOST,
        )

except Exception as e:
    
    get_logger(LogType.Cache).critical('Cache system not connected: ' + e)
