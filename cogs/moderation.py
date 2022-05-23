import discord

from discord import app_commands
from discord.ext import commands
from discord.app_commands import Group, ContextMenu

from data.config import Assets, Channel, Config
from modules.utils import error_embed, success_embed


class MainModeration(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client
    
    mod = Group(name="mod", description="Moderator commands", guild_ids=[Config.SERVER_ID])

    mod_qanda = mod.gr(name="qanda", description="Qanda moderator commands", guild_ids=[Config.SERVER_ID])

    @mod_qanda.command(name="ping", description="Ping the bot", guild_ids=[Config.SERVER_ID])
    async def mod_qanda_test(self, ctx:commands.Context):
        ctx.send("Pong!")



async def setup(client:commands.Bot):
    await client.add_cog(MainModeration(client))