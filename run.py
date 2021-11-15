import os

from discord import Intents
from discord.ext.commands import Bot

from modules.config import Env


def run_discord_client():
    
    client = Bot(
        help_command=None,
        command_prefix='!',
        intents=Intents().all()
    )

    for path, subdirs, files in os.walk('cogs/'):
        for name in files:
            if name.endswith('.py'):
                filename = os.path.join(path, name).replace('/', '.').replace('\\', '.')[:-3]

                client.load_extension(filename)
        
    
    print('Loaded extensions --> ' + ', '.join(client.extensions.keys()))

    client.run(Env.TOKEN)



if __name__ == '__main__':
    run_discord_client()



