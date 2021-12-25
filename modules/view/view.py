import discord

from discord.ext import commands

class PersistentView(discord.ui.View):
    def __init__(self, **kwargs):
        super().__init__(timeout=None)
        self.__dict__.update(kwargs)