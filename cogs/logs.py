import discord
import time
from discord.ext import commands
from datetime import datetime

from modules.database.models import MemberModel
from data.config import Channel


class Logs(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client


    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        print(f'{member} joined the server')
        member_model = await MemberModel.find_one(MemberModel.member_id == member.id)
        if not member_model:
            member_model = MemberModel(
                member_id = member.id,
                latest_discord_id = member.name,
                is_robot= True if member.bot else False,
            )
            await member_model.save()
        else:
            member_model.is_leaved == False
            member_model.leaved_at == None
            await member_model.save()
        
        log_channel = self.client.get_channel(Channel.JOIN_LOG)
        timestamp = time.mktime(member.joined_at.timetuple())
        em = discord.Embed(
            description=f'{member.mention} joined the server.\n- id: {member.id}\n- join at: <t:{timestamp}:F>',
            colour=discord.Colour.green()
        )
        await log_channel.send(
            embed=em
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member:discord.Member):
        print(f'{member} joined the server')
        member_model = await MemberModel.find_one(MemberModel.member_id == member.id)
        if member_model:
            member_model.is_leaved == True
            member_model.leaved_at = datetime.now()
            await member_model.save()
        
        log_channel = self.client.get_channel(Channel.LEAVE_LOG)
        timestamp = time.mktime(datetime.now().timetuple())
        em = discord.Embed(
            description=f'{member.mention} leaved the server.\n- id: {member.id}\n- leaved at: <t:{timestamp}:F>',
            colour=discord.Colour.green()
        )
        await log_channel.send(
            embed=em
        )

async def setup(client:commands.Bot):
    await client.add_cog(Logs(client))