import sys

from rom import util
from redis import exceptions

from modules.config import Env
from modules.cache import PlayTime


__all__ = ['init_cache']


def init_cache():

    util.set_connection_settings(
        host=Env.CACHE_HOST,
        port=6379,
        db=0,
    )
    client = util.get_connection()

    try:
        info = client.info()
        print(' └ Cache server is alive. Redis version: ' + info['redis_version'])
        for i in PlayTime.query.all():
            i.delete()
    except exceptions.ConnectionError:
        print('> Cache server is not available.')
        print('> Exiting...')
        sys.exit(1)
    
    except exceptions.AuthenticationError:
        print('> Cache server authentication failed.')
        print('> Exiting...')
        sys.exit(1)