import os

from discord import Intents, Client
from discord.ext.commands import Bot, when_mentioned_or

from modules.config import Env
from modules.utils import get_logger, LogType
from data.config import Config

class PPClient(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(
            help_command = None,
            command_prefix = when_mentioned_or('!'),
            Intents = Intents().all(),
            )

    async def on_ready(self):
        get_logger(LogType.PT).debug('Player Tracker is online!')
        print('Bot is run!')

def run_discord_client():

    client = PPClient()

    # Load presistent views
    print('Loading persistent views...')
    if len(Config.list_view_classes) != 0:
        for view in Config.list_view_classes:
            client.add_view(view)
        client.persistent_views_added = True

        get_logger(LogType.DEBUG).debug(
            'Presistent views --> ' + ', '.join(Config.list_view_classes)
        )
    else:
        get_logger(LogType.DEBUG).debug(
            'No views loaded'
        )

    # Load extentions
    print('Loading extentions...')
    for path, subdirs, files in os.walk('cogs/'):
        for name in files:
            if name.endswith('.py'):
                filename = os.path.join(path, name).replace('/', '.').replace('\\', '.')[:-3]

                client.load_extension(filename)
        
    get_logger(LogType.DEBUG).debug(
        'Loaded extensions --> ' + ', '.join(client.extensions.keys())
    )

    return client.run(Env.TOKEN) # Run Client

if __name__ == '__main__':
    run_discord_client()