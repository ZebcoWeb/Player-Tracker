import os

from discord import Intents
from discord.ext.commands import Bot, when_mentioned_or

from modules.database import signals
from modules.config import Env
from modules.utils import get_logger, LogType



def load_persistent_views(client):
    list_view_classes = [
        #! list presistent view here
    ]
    if list_view_classes.count() !=0:
        for view in list_view_classes:
            client.add_view(view)
    client.persistent_views_added = True
    get_logger(LogType.DEBUG).debug(
        'Presistent views --> ' + ', '.join(list_view_classes)
    )

def load_extentions(client):
    for path, subdirs, files in os.walk('cogs/'):
        for name in files:
            if name.endswith('.py'):
                filename = os.path.join(path, name).replace('/', '.').replace('\\', '.')[:-3]

                client.load_extension(filename)
        
    get_logger(LogType.DEBUG).debug(
        'Loaded extensions --> ' + ', '.join(client.extensions.keys())
    )


def run_discord_client():

    class PPClient(Bot):
        def __init__(self):
            super().__init__(
                help_command = None,
                command_prefix = when_mentioned_or('!'),
                Intents = Intents().all(),
                persistent_views_added = False,
                )
        
        async def on_ready(self):

            get_logger(LogType.DEBUG).debug('Loading persistent views...')
            load_persistent_views(self)

            get_logger(LogType.DEBUG).debug('Loading extentions...')
            load_extentions(self)

            get_logger(LogType.PT).debug('Player Tracker is online!')


    client = PPClient()

    client.run(Env.TOKEN)

if __name__ == '__main__':
    run_discord_client()



