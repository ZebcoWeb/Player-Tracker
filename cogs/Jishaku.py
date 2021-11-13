from jishaku.cog import Jishaku
from discord.ext import commands




def setup(client: commands.Bot):
    
    client.add_cog(Jishaku(bot=client))