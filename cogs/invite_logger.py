import discord
import copy

from discord.ext import commands

from data.config import Config
from modules.utils import error_embed, success_embed
from modules.models import MemberModel


class InviteLogger(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client
        self.invites = None
    
    async def cog_load(self):
        await self.load_invites()

    async def load_invites(self):
        guild = await self.client.fetch_guild(Config.SERVER_ID)
        self.invites = await guild.invites()

    def find_invite_by_code(self, inv_list, code):
        for inv in inv_list:
            if inv.code == code:
                return inv

    @commands.Cog.listener('on_member_join')
    async def set_invite_count(self, member:discord.Member):
        invs_before = self.invites
        invs_after = await member.guild.invites()
        self.invites = invs_after
        for invite in invs_before:
            if invite.uses < self.find_invite_by_code(invs_after, invite.code).uses:
                if invite.inviter.bot == False and member != invite.inviter:
                    await MemberModel.find_one(MemberModel.member_id == invite.inviter.id).inc({MemberModel.invite_count: 1})


async def setup(client:commands.Bot):
    await client.add_cog(InviteLogger(client))