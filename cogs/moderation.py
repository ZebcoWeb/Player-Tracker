import discord

from discord.channel import TextChannel
from discord.ext import commands

from data.config import Assets, Channel, Config
from modules.utils import error_embed, success_embed
from modules.view import CreateRoomView


class MainModeration(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client

    # @commands.slash_command(name='clear', description='Clear messages', guild_ids=[Config.SERVER_ID])
    # async def clear(
    #     self,
    #     ctx: ApplicationContext,
    #     limit: Option(int, 'Enter the value'),
    #     oldest_first: Option(bool, 'oldest first', required=False, default=False),
    #     ) -> None:
    #     async with ctx.typing():
    #         await ctx.channel.purge(limit=limit, oldest_first=oldest_first )
    #     await ctx.delete()
    

async def setup(client:commands.Bot):
    await client.add_cog(MainModeration(client))