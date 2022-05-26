import discord
import copy

from discord import ButtonStyle, Interaction

from data.config import Emoji
from modules.models import RoomModel, MemberModel
from modules.utils import error_embed



class LikeButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            style=ButtonStyle.red,
            label=  None,
            emoji=Emoji.LIKE
        )
    
    async def callback(self, interaction: Interaction):
        room = await RoomModel.find_one(RoomModel.tracker_msg_id == interaction.message.id, fetch_links=True)
        # user = await MemberModel.find_one(MemberModel.member_id == interaction.user.id)
        if room:
            if interaction.user.id in room.likes:
                await self.dislike_handler(interaction)
                room.likes.remove(interaction.user.id)
                await room.save()
            else:
                await self.like_handler(interaction)
                room.likes.append(interaction.user.id)
                await room.save()
        else:
            await interaction.response.send_message(
                embed=error_embed('This room is already closed'),
                ephemeral=True
            )
        
    def calculate_likes(self):
        if self.label is None:
            return 0
        else:
            return int(self.label)
    
    async def like_handler(self, interaction: Interaction):
        view = self.view
        new_button = copy.copy(self)
        new_button.label = str(self.calculate_likes() + 1)
        view.remove_item(self)
        view.add_item(new_button)
        await interaction.response.edit_message(view=view)

    async def dislike_handler(self, interaction: Interaction):
        view = self.view
        new_button = copy.copy(self)
        new_button.label = str(self.calculate_likes() - 1)
        if new_button.label == '0':
            new_button.label =  None
        view.remove_item(self)
        view.add_item(new_button)
        await interaction.response.edit_message(view=view)