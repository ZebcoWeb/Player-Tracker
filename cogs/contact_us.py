import discord
import asyncio

from discord.ext import commands
from discord import app_commands
from discord.app_commands import Group

from data.config import Config, Category, Channel, Assets
from modules.view import ContactUsForm, ContextView
from modules.utils import error_embed


class ContactUs(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client

    contact = Group(name='contact_us', description='💬 Contact us commands', guild_ids=[Config.SERVER_ID])

    @contact.command(name='new', description='💬 Open new ticket')
    async def contact_us_new(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ContactUsForm(self.client))


    @contact.command(name='context', description='💬 send context (admin only)')
    @app_commands.checks.has_permissions(manage_channels=True)
    async def contact_us_context(self, interaction: discord.Interaction):

        channel = await self.client.fetch_channel(Channel.CONTACT_US)

        async for message in channel.history():
            await message.delete()
        em = discord.Embed(
            description= "**Looking for a way to contact us?** Fill out the support form by clicking the button and wait for the admins to respond.\n\n**NOTE:** Don't send spam or unnecessary content, you will be penalized if repeated.",
            color=Config.BRAND_COLOR
        )
        em.set_author(name='Support section', icon_url=Assets.SUPPORT)
        em.set_image(url=Assets.SUPPORT_BANNER)
        await channel.send(embed=em, view=ContextView())
        await interaction.response.defer()


    @contact.command(name='close', description='Close ticket (admin only)')
    @app_commands.describe(channel='Channel to close the ticket (Optional)')
    @app_commands.checks.has_permissions(manage_channels=True)
    async def contact_us_close(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
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