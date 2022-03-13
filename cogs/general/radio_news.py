import discord
from discord.ext import commands

from data.config import Channel



class RadioNews(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        if message.channel.id == Channel.RADIO_NEWS and message.author.bot:
            thread = await message.create_thread(
                name = '💭 Comments'
            )
            await thread.edit(
                slowmode_delay = 5
            )
            await thread.leave()

def setup(client:commands.Bot):
    client.add_cog(RadioNews(client))