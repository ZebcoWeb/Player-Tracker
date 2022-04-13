import discord
import time
from discord.ext import commands
from datetime import datetime

from modules.database.models import MemberModel
from data.config import Channel, Config


class Member(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client
        self.client.loop.create_task(self.leftover_members())



    async def leftover_members(self):
        guild = await self.client.fetch_guild(Config.SERVER_ID)
        registered_members = await MemberModel.members_id_list()
        async for member in guild.fetch_members(limit=None):
            if member.id not in registered_members:
                await MemberModel.join_member(member)

    # Event listeners
    @commands.Cog.listener('on_member_join')
    async def register_new_member(self, member: discord.Member):
        await MemberModel.join_member(member)
        log_channel = await self.client.fetch_channel(Channel.JOIN_LOG)
        timestamp = round(time.mktime(member.joined_at.timetuple()))
        em = discord.Embed(
            title=f'📥 **{member.name}#{member.discriminator}** joined the server',
            description=f'\n> **Member ID:** `{member.id}`\n> **join at:** <t:{timestamp}:F>\n> **Mention:** {member.mention}',
            colour=discord.Colour.green()
        )
        em.set_thumbnail(url=member.display_avatar.url)
        await log_channel.send(
            embed=em
        )

    @commands.Cog.listener('on_member_remove')
    async def register_leaved_member(self, member:discord.Member):
        await MemberModel.leave_member(member)
        log_channel = await self.client.fetch_channel(Channel.LEAVE_LOG)
        timestamp = round(time.mktime(datetime.now().timetuple()))
        em = discord.Embed(
            title=f'📤 **{member.name}#{member.discriminator}** left the server',
            description=f'\n> **Member ID:** `{member.id}`\n> **leaved at:** <t:{timestamp}:F>',
            colour=discord.Colour.green()
        )
        em.set_thumbnail(url=member.display_avatar.url)
        await log_channel.send(
            embed=em
        )

async def setup(client:commands.Bot):
    await client.add_cog(Member(client))