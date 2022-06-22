import discord

from datetime import datetime, timedelta
from discord import app_commands
from discord.ext import commands

from data.config import Config, Role
from modules.utils import error_embed, success_embed
from modules.models import MemberModel


class MainModeration(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client


    @app_commands.command(name='ban', description='🚫 Ban a user (admin only)')
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guilds(Config.SERVER_ID)
    @app_commands.describe(user='User to ban', period='Time for ban ( 0 for forever or another number (1,2,3) for hours)', reason=' Reason for banning')
    async def ban(self, interaction: discord.Interaction, user: discord.Member, period: int, *, reason: str):
        member = await MemberModel.find_one(MemberModel.member_id == user.id)
        if not member.is_staff:
            if not member.is_ban:
                if period >= 0:
                    if period == 0:
                        member.is_ban_forever = True
                    else:
                        member.ban_time = datetime.now() + timedelta(hours=period)
                    await member.save()
                    try:
                        ban_notice = 'You have been banned from **Player Tracker** server {}'.format(f'for {period} hours.' if period != 0 else 'forever.') + '\n**Reason:** "*{reason}*\n\n⚖️ You can contact support to lift the ban."'
                        await user.send(embed=error_embed(ban_notice))
                    except:
                        pass
                    await interaction.response.send_message(embed=success_embed(f'User {user.mention} banned successfully\n**- Reason:** *{reason}*'))
                else:
                    await interaction.response.send_message(embed=error_embed('Period must be **greater than 0**'))
            else:
                await interaction.response.send_message(embed=error_embed(f"User {user.mention} is already banned"))
        else:
            await interaction.response.send_message(embed=error_embed(f"You can't ban a staff member"))
    
    
    @app_commands.command(name='unban', description='🚫 Unban a user (admin only)')
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guilds(Config.SERVER_ID)
    @app_commands.describe(user='User to ban')
    async def unban(self, interaction: discord.Interaction, user: discord.Member):
        member = await MemberModel.find_one(MemberModel.member_id == user.id)
        if member.is_ban:
            member.is_ban_forever = False
            member.ban_time = None
            await member.save()
            try:
                await user.send(embed=success_embed('You have been unbanned from **Player Tracker** server'))
            except:
                pass
            await interaction.response.send_message(embed=success_embed(f'User {user.mention} unbanned successfully'))
        else:
            await interaction.response.send_message(embed=error_embed(f"User {user.mention} is not banned"))
    

    @app_commands.command(name='set_ram', description='🚫 Set a user\'s RAM (owner only)')
    @app_commands.checks.has_role(Role.CPU)
    @app_commands.guilds(Config.SERVER_ID)
    @app_commands.describe(user='User to set role')
    async def unban(self, interaction: discord.Interaction, user: discord.Member):
        ram_role = user.get_role(Role.RAM)
        if ram_role:
            await interaction.response.send_message(embed=error_embed('Member already has a RAM role'))
        else:
            member = await MemberModel.find_one(MemberModel.member_id == user.id)
            member.is_staff = True
            await member.save()
            await user.add_roles(ram_role)
            await interaction.response.send_message(embed=success_embed(f'User {user.mention} has been set to RAM'))


    @app_commands.command(name='set_graphic_card', description='🚫 Set a user\'s Graphic Card (owner only)')
    @app_commands.checks.has_role(Role.CPU)
    @app_commands.guilds(Config.SERVER_ID)
    @app_commands.describe(user='User to set role')
    async def unban(self, interaction: discord.Interaction, user: discord.Member):
        graphic_card__role = user.get_role(Role.GRAPHIC_CARD)
        if graphic_card__role:
            await interaction.response.send_message(embed=error_embed('Member already has a Graphic Card role'))
        else:
            member = await MemberModel.find_one(MemberModel.member_id == user.id)
            member.is_staff = True
            await member.save()
            await user.add_roles(graphic_card__role)
            await interaction.response.send_message(embed=success_embed(f'User {user.mention} has been set to Graphic Card'))

    @commands.hybrid_command(name='clear', description='🧹 Clear messages')
    @app_commands.guilds(Config.SERVER_ID)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(number='Number of messages to clear [0 for clear all]')
    async def clear_messages(self, ctx: commands.Context, number: int):
        try:
            if number == 0:
                messages_number = len([message async for message in ctx.channel.history(limit=None)])
                if ctx.interaction:
                    await ctx.channel.purge(limit=messages_number, bulk=True)
                    await ctx.interaction.response.send_message(
                        embed=success_embed(f'{messages_number} messages cleared'),
                        ephemeral=True
                    )
                else:
                    await ctx.channel.purge(limit=messages_number + 1, bulk=True)
            else:
                if ctx.interaction:
                    await ctx.channel.purge(limit=number, bulk=True)
                    await ctx.interaction.response.send_message(
                        embed=success_embed(f'{number} messages cleared'),
                        ephemeral=True
                    )
                else:
                    await ctx.channel.purge(limit=number + 1, bulk=True)
        except Exception as e:
            pass 


async def setup(client:commands.Bot):
    await client.add_cog(MainModeration(client))