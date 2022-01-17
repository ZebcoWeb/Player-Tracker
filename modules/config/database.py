import sys, motor, asyncio

from beanie import init_beanie

from modules.utils import inspect_models
from modules.config import Env


__all__ = ['init_database']


async def init_database(loop: asyncio.AbstractEventLoop = None):
    
    client = motor.motor_asyncio.AsyncIOMotorClient(
        host=Env.DATABASE_HOST,
        port=27017,
        username=Env.DATABASE_USER,
        password=Env.DATABASE_PASSWORD,
        io_loop=loop,
        connectTimeoutMS=15000 # 15 seconds
    )
    
    try:
        info = await client.server_info()

        if info['ok'] == 1.0:

            models = inspect_models()

            await init_beanie(
                database= client[Env.DATABASE_DB],
                document_models= models
            )
            print(' └ Database is alive. MongoDB version: ' + info['version'] + f'\n └ {len(models)} models were activated in the database!')
            
        else:
            print('└ Database is not alive!')
            sys.exit(1)

    except Exception as e:

        print('> Could not connect to database!')
        print('> Exiting...')
        sys.exit(1)

