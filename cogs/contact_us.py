import discord
import asyncio

from discord.ext import commands
from discord import app_commands
from discord.app_commands import Group

from data.config import Config, Category
from modules.view import ContactUsForm
from modules.utils import success_embed, error_embed


class ContactUs(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client

    @app_commands.command(name='contact', description='💬 Contact us')
    @app_commands.guilds(Config.SERVER_ID)
    async def contact_us(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ContactUsForm(self.client))


    @app_commands.command(name='close', description='Close ticket')
    @app_commands.describe(channel='Channel to close the ticket (Optional)')
    @app_commands.checks.has_permissions(manage_channels=True)
    async def contact_us(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        if channel is None:
            channel = interaction.channel

        ticket_category = await self.client.fetch_channel(Category.TICKETS)

        if channel in ticket_category.channels:
            em = discord.Embed(
                title="Thanks for giving your time!",
                description='We are closing this ticket automatically in 10 seconds...',
                color=Config.BRAND_COLOR
            )
            await interaction.response.defer()
            message = await channel.send(embed=em)
            await message.add_reaction('🇹')
            await asyncio.sleep(1)
            await message.add_reaction('🇭')
            await asyncio.sleep(1)
            await message.add_reaction('🇽')
            await asyncio.sleep(8)
            await channel.delete()
        else:
            await interaction.response.send_message(
                embed=error_embed(f'Ticket channel not found'), 
                ephemeral=True
            )


async def setup(client:commands.Bot):
    await client.add_cog(ContactUs(client))