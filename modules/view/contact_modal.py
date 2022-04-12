import discord

from discord.ui import TextInput

from data.config import Category, Role, Emoji
from modules.utils import success_embed
from modules.database import MemberModel
    

class ContactUsForm(discord.ui.Modal):
    def __init__(self, client: discord.Client):
        self.client = client

        super().__init__(
            title="Enter your message for contact us",
            custom_id="contact_us_modal",
            timeout=200
        )
        self.add_item(
            TextInput(
                style= discord.TextStyle.short,
                label='Subject',
                placeholder="What's your message subject? Be specific",
                custom_id='contact_us_subject_input',
                min_length = 5,
                max_length = 120,
                required = True,
            )
        )
        self.add_item(
            TextInput(
                style= discord.TextStyle.long,
                label='Message',
                placeholder='Enter your message here...',
                custom_id='contact_us_message_input',
                min_length = 10,
                max_length = 600,
                required = True,
            )
        )
    

    async def on_submit(self, interaction: discord.Interaction):
        subject = discord.utils.get(self.children, custom_id='contact_us_subject_input').value
        message = discord.utils.get(self.children, custom_id='contact_us_message_input').value
        guild = interaction.guild
        member_model = await MemberModel.find_one(MemberModel.member_id == interaction.user.id)
        category = await self.client.fetch_channel(Category.TICKETS)
        user = await self.client.fetch_user(member_model.member_id)
        ram_role = guild.get_role(Role.RAM)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
            ram_role: discord.PermissionOverwrite(read_messages=True, send_messages=False, manage_messages=True),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, )
        }
        ticket_channel = await category.create_text_channel(
            name=f'{user.display_name}',
            overwrites=overwrites,

        )
        em = discord.Embed(
            title=f'{Emoji.CIRCLE} {subject}',
            description=f'*{message}*\n\u200b',
            color=discord.Color.blue()
        )
        em.set_thumbnail(url=user.display_avatar.url)
        await ticket_channel.send(embed=em, content=f'{user.mention}')

        await interaction.response.send_message(
            embed = success_embed(f"Your ticket has been created successfully: {ticket_channel.mention}\n\n- Please be patient while team members handle this ticket."),
            ephemeral=True
        )