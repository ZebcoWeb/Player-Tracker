from rom import util

from modules.utils.enums import LogType
from modules.utils import get_logger
from modules.config import Env

try:

    util.set_connection_settings(
        host=Env.CACHE_HOST,
        )

except Exception as e:
    
    get_logger(LogType.Cache).critical('Cache system not connected: ' + e)
