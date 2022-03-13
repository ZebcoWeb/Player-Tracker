import inspect
import sys

from discord import Intents, __version__, InteractionResponse
from discord.ext.commands import Bot, when_mentioned_or

from data.config import Config
from modules.config import Env, init_database
from modules.database.models import GameModel
from modules.utils import LogType, get_logger, load_extentions
from modules.view import PersistentView


class BotClient(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(
            help_command = None,
            command_prefix = when_mentioned_or('!'),
            Intents = Intents().all()
        )
        self.persistent_views_added = False

    async def on_ready(self):

        # Load all active games from database
        print('> Loading games...')
        self.games = await GameModel.active_games(ignore_cache=True)
    
         # Load extentions
        print('> Loading extentions...')
        load_extentions(self)

        # Loading persistent views
        print('> Loading persistent views...')
        views_added = []

        for name, obj in inspect.getmembers(sys.modules['modules.view']):
            if inspect.isclass(obj) and issubclass(obj, PersistentView):

                # Specials (Be sure to come with kwargs)
                if name == 'CreateRoomView' or 'QandaView':
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

    print('\n> Starting...')
    client = BotClient()

    # Set up the database and check the connection status
    print('> Check the database connection...')
    client.loop.run_until_complete(init_database(loop=client.loop))

    # Run the client
    return client.run(Env.TOKEN) # Run Client

if __name__ == '__main__':
    run_discord_client()


# سلطان کد زنی نامنظم