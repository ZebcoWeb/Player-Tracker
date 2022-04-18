import discord
import asyncio

from discord import ButtonStyle

from data.config import Emoji
from modules.database import RoomModel
from modules.utils.functions import success_embed




class RoomDashboard(discord.ui.Select):
    def __init__(self) -> None:
        super().__init__(
            placeholder=f'Room Dashboard (ya, u can be an admin!)',
        )

        self.add_option(
            label='Delete my room',
            emoji=Emoji.RED_BIN,
            value='delete_room'
        )
    
    async def callback(self, interaction: discord.Interaction):
        value_selected = self.values[0]

        if value_selected == 'delete_room':
            await self.delete_room(interaction)

    
    async def delete_room(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            embed=success_embed(
                'Your room will be closed for another 10 seconds...\n\nㅤㅤ***Good Game!***'
            ),
            view=None
        )
        await asyncio.sleep(10)
        room = await RoomModel.find_one(RoomModel.room_create_channel_id == interaction.channel.id)
        await room.full_delete_room(interaction.client)
        

class RoomUserPanel(discord.ui.View):
    def __init__(self, invite_link: str):
        self.invite_link = invite_link
        super().__init__(timeout=None)
        self.add_item(
            discord.ui.Button(
                label='ㅤJoin Roomㅤ',
                style=ButtonStyle.url,
                url=self.invite_link,
            )
        )
    
    @discord.ui.button(label='Dashboard', style=ButtonStyle.blurple, emoji=Emoji.MENU)
    async def callback_dashboard(self, interaction: discord.Interaction, button: discord.ui.Button):
        dashboard_view = discord.ui.View(timeout=None)
        dashboard_view.add_item(RoomDashboard())
        await interaction.response.edit_message(view=dashboard_view)