import discord
from discord.ext import commands

from data.config import Config, Role


class PlayingNow(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client
        self.guild = self.client.get_guild(Config.SERVER_ID)


    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        print('me!')
        try:
            playing_role = self.guild.get_role(Role.PLAYING_NOW)
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
                else:
                    pass
            else:
                pass
        except discord.errors.Forbidden:
            pass

def setup(client:commands.Bot):
    client.add_cog(PlayingNow(client))