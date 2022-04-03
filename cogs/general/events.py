import discord
from discord.ext import commands

from data.config import Config, Role, Channel


class Event(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client
    #     self.guild = self.client.fetch_guild(Config.SERVER_ID)


    # # Playing Now event
    # @commands.Cog.listener()
    # async def on_member_update(self, before, after):
    #     try:
    #         playing_role = self.guild.get_role(Role.PLAYING_NOW)
    #         if after.activity:
    #             if isinstance(after.activity , discord.Game):
    #                 if playing_role not in after.roles:
    #                     await after.add_roles(playing_role)
    #             else:
    #                 if playing_role in after.roles:
    #                     await after.remove_roles(playing_role)
    #         elif after.activity == None:
    #             if playing_role in after.roles:
    #                 await after.remove_roles(playing_role)
    #     except discord.errors.Forbidden:
    #         pass
    
    
    # Radio News event
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


async def setup(client:commands.Bot):
    await client.add_cog(Event(client))