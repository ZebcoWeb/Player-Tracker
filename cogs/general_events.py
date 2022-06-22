import discord
from discord.ext import commands

from data.config import Config, Role, Channel


class Event(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client


    # Playing Now event
    @commands.Cog.listener('on_member_update')
    async def playing_now_role_event(self, before, after):
        guild = await self.client.fetch_guild(Config.SERVER_ID)
        try:
            playing_role = guild.get_role(Role.PLAYING_NOW)
            if after.activity:
                if isinstance(after.activity , discord.Game):
                    if playing_role not in after.roles:
                        await after.add_roles(playing_role)
                else:
                    if playing_role in after.roles:
                        await after.remove_roles(playing_role)
            elif after.activity == None:
                if playing_role in after.roles:
                    await after.remove_roles(playing_role)
        except Exception as e:
            print(e)
    
    
    # Radio News event
    @commands.Cog.listener('on_message')
    async def set_comments_to_news(self, message:discord.Message):
        if message.channel.id == Channel.RADIO_NEWS and message.author.bot:
            thread = await message.create_thread(
                name = '💭 Comments'
            )
            await thread.edit(
                slowmode_delay = 5
            )
            await thread.leave()


    # Reaction for suggestions event
    @commands.Cog.listener('on_message')
    async def add_reaction_for_suggestion(self, message:discord.Message):
        if message.channel.id == Channel.SUGGESTIONS and not message.author.bot:
            if not message.reference:
                await message.add_reaction('👍')
                await message.add_reaction('👎')


async def setup(client:commands.Bot):
    await client.add_cog(Event(client))