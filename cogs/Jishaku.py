from discord.ext import commands
from jishaku.cog import Jishaku



async def setup(bot: commands.Bot):
    await bot.add_cog(Jishaku(bot=bot))