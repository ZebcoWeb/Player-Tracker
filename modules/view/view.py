import discord

from discord.ext import commands


class PersistentView(discord.ui.View):
    def __init__(self, client: commands.Bot):
        super().__init__(timeout=None)
        client.add_view(self)
        client.persistent_views_added = True