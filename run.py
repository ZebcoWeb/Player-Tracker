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
    
    loaded_extensions = {}

    for path, subdirs, files in os.walk('cogs/'):
        for name in files:
            if name.endswith('.py'):
                filename = os.path.join(path, name).replace('/', '.').replace('\\', '.')[:-3]
                cog_name = name[:-3].split('.')[-1]
                
                loaded_extensions[cog_name] = filename

                client.load_extension(filename)

                print(f"\n- Loaded {filename}")

    client.run(Env.TOKEN)



if __name__ == '__main__':
    run_discord_client()



