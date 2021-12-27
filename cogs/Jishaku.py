from discord.ext import commands
from jishaku.cog import Jishaku


def setup(client: commands.Bot):
    
    client.add_cog(Jishaku(bot=client))