import discord
import time
from discord.ext import commands
from datetime import datetime, timedelta

from modules.database.models import MemberModel, RoomModel
from modules.cache import PlayTime
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
    
    @commands.Cog.listener('on_voice_state_update')
    async def room_play_time(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
            if after.channel:
                channel = after.channel
            else:
                channel = before.channel
            room_model = await RoomModel.find(RoomModel.room_voice_channel_id == channel.id, fetch_links=True).to_list()
            if room_model != []:
                room_model = room_model[0]
                if after.channel:
                    PlayTime(
                        member_id=member.id,
                        room_id=channel.id,
                    ).save()
                elif before.channel:
                    play_status = PlayTime.get_by(member_id=member.id)
                    if play_status:
                        playtime = datetime.now() - play_status.join_time
                        if playtime > timedelta(minutes=1):
                            member_model = room_model.creator
                            game_model = member_model.game
                            member_model.total_play_time += playtime
                            game_model.total_play_time += playtime
                            await member_model.save()
                            await game_model.save()
                            play_status.delete()


async def setup(client:commands.Bot):
    await client.add_cog(Member(client))