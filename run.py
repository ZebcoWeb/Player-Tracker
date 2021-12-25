import os
import sys
import inspect

from discord import Intents, __version__
from discord.ext.commands import when_mentioned_or, Bot

# local modules
from modules.config import Env
from modules.view import PersistentView
from modules.database.models import GameModel
from modules.utils import get_logger, LogType, db_is_alive
from data.config import Config

class PPClient(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(
            help_command = None,
            command_prefix = when_mentioned_or('!'),
            Intents = Intents().all(),
            )
        self.persistent_views_added = False

    async def on_ready(self):
        print('> Loading persistent views...')
        views_added = []
        for name, obj in inspect.getmembers(sys.modules['modules.view']):
            if inspect.isclass(obj) and issubclass(obj, PersistentView):

                # Specials (Be sure to come with kwargs)
                if name == 'CreateRoomView':
                    self.add_view(obj(client = self))

                # Others
                else:
                    self.add_view(obj())
                    views_added.append(name)

        self.persistent_views_added = True

        print(f"""
        
 ____    ______      ____    _____   ______   
/\  _`\ /\__  _\    /\  _`\ /\  __`\/\__  _\  
\ \ \L\ \/_/\ \/    \ \ \L\ \ \ \/\ \/_/\ \/  
 \ \ ,__/  \ \ \     \ \  _ <\ \ \ \ \ \ \ \  
  \ \ \/    \ \ \     \ \ \L\ \ \ \_\ \ \ \ \ 
   \ \_\     \ \_\     \ \____/\ \_____\ \ \_\\
    \/_/      \/_/      \/___/  \/_____/  \/_/
                                              
                                              
                                            
> Player Tracker discord robot is running!
    - Applicaion id -> {self.application_id}
    - Pong -> {round(self.latency * 1000)} ms
    - Player Tracker version -> {Config.VERSION}
    - Pycord version -> {__version__}
    
""")
        print('> Loaded extensions --> ' + ', '.join(self.extensions.keys()))
        print('> Loaded persistent views --> ' + ', '.join(pview for pview in views_added))
        print('> Number of games loaded --> ' + str(len(self.games)))

def run_discord_client():

    client = PPClient()

    # Load extentions
    print('> Loading extentions...')

    for path, subdirs, files in os.walk('cogs/'):
        for name in files:
            if name.endswith('.py'):
                filename = os.path.join(path, name).replace('/', '.').replace('\\', '.')[:-3]

                try:
                    client.load_extension(filename)
                except:
                    pass

    print('> Check the database connection...')
    db_is_alive()

    print('> Loading games...')
    client.games = GameModel.objects.filter(is_active = True)

    return client.run(Env.TOKEN) # Run Client

if __name__ == '__main__':

    run_discord_client()