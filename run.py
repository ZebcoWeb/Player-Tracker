import sys
import inspect
import discord

from discord import Intents, __version__
from discord.ext.commands import Bot, when_mentioned_or

from data.config import Config
from modules.config import Env, init_database, init_cache
from modules.models import GameModel, QandaModel, LangModel
from modules.utils import load_extentions, load_ctxs

from modules.view import PersistentView



class BotClient(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(
            help_command = None,
            command_prefix = when_mentioned_or('!'),
            intents=Intents.all()
        )
        self.persistent_views_added = False


    async def setup_hook(self) -> None:

        
        # Set up the database and check the connection status
        print('> Check the database connection...')
        await init_database(loop=self.loop)

        # Set up the cache
        print('> Initializing cache...')
        init_cache()

        self.ctx_menus = []

        # Load extentions
        print('> Loading extentions...')
        await load_extentions(self)

        # Load context menus
        print('> Loading Context menus...')
        load_ctxs(self.tree, self.ctx_menus)
            

    async def on_ready(self):

        await self.change_presence(status=discord.Status.online)
        
        # Sync the tree commands
        await self.tree.sync(guild=discord.Object(id=Config.SERVER_ID))

        # Load Cache datas
        print('> Loading cache datas...')
        self.games = await GameModel.trend_games(ignore_cache=True)
        self.qanda_games = await QandaModel.games(ignore_cache=True)
        self.langs = await LangModel.active_langs(ignore_cache=True)

        # Loading persistent views
        print('> Loading persistent views...')
        views_added = []
        for name, obj in inspect.getmembers(sys.modules['modules.view']):
            if inspect.isclass(obj) and issubclass(obj, PersistentView):

                # Specials (Be sure to come with kwargs)
                if name == 'CreateRoomView' or 'QandaView':
                    self.add_view(obj(client = self))
                    views_added.append(name)
                # Others
                else:
                    self.add_view(obj())

        self.persistent_views_added = True

        print(f"""
        

 ______     __  __     ______     _____     ______     __   __    
/\  ___\   /\ \_\ \   /\  __ \   /\  __-.  /\  __ \   /\ "-.\ \   
\ \___  \  \ \  __ \  \ \ \/\ \  \ \ \/\ \ \ \  __ \  \ \ \-.  \  
 \/\_____\  \ \_\ \_\  \ \_____\  \ \____-  \ \_\ \_\  \ \_\" \_\ 
  \/_____/   \/_/\/_/   \/_____/   \/____/   \/_/\/_/   \/_/ \/_/ 


                                            
> SHODAN discord robot is running! (Player Tracker)
    - Applicaion id -> {self.application_id}
    - Pong -> {round(self.latency * 1000)} ms
    - SHODAN version -> {Config.VERSION}
    - Library version -> {__version__}
    
""")
        print('> Loaded extensions --> ' + ', '.join(self.extensions.keys()))
        print('> Loaded persistent views --> ' + ', '.join(pview for pview in views_added))
        print('> Number of games loaded --> ' + str(len(self.games)))

def run_discord_client():

    print('\n> Starting...')
    client = BotClient()

    # Run the client
    return client.run(Env.TOKEN)

if __name__ == '__main__':
    run_discord_client()




# سلطان کد زنی نامنظم