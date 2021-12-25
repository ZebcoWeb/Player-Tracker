import discord

from discord import ButtonStyle, Colour, Embed

from .view import PersistentView

from data.config import Emoji

class TaskDeleteAgain(PersistentView):

    @discord.ui.button(label='Delete Task', custom_id='delete_button', style=ButtonStyle.red, emoji=Emoji.BIN_TONE)
    async def done_task(self, button: discord.ui.Button, interaction: discord.Interaction):

        await interaction.message.delete()
        await interaction.response.defer()

class TaskView(PersistentView):

    @discord.ui.button(label='Done task', custom_id='done_button', style=ButtonStyle.green, emoji=Emoji.CHECK_CIRCLE_TONE)
    async def done_task(self, button: discord.ui.Button, interaction: discord.Interaction):

        new_embed: Embed = interaction.message.embeds[0]
        new_embed.description += '\n\n- `✅ Done`'
        new_embed.color = Colour.green()

        await interaction.response.edit_message(embed=new_embed, view=None)
    
    @discord.ui.button(label='Cancel Task', custom_id='cancel_button', style=ButtonStyle.red, emoji=Emoji.CANCEL_CIRCLE_TONE)
    async def cancel_task(self, button: discord.ui.Button, interaction: discord.Interaction):

        new_embed: Embed = interaction.message.embeds[0]
        new_embed.description = f'~~{new_embed.description}~~'
        new_embed.color = Colour.default()

        await interaction.response.edit_message(embed=new_embed, view=TaskDeleteAgain())