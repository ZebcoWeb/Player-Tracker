import discord

from datetime import datetime
from discord.ui import TextInput, Button

from data.config import Channel, Emoji
from modules.models import QandaModel, MemberModel
from beanie.odm.operators.update.general import Inc
from modules.utils import is_ban_handler, is_inviter_handler, success_embed, is_media, checks

from .view import PersistentView


class QandaView(PersistentView):
    def __init__(self, client: discord.Client):
        self.client = client
        super().__init__(timeout=None)
    
    @discord.ui.button(label='ㅤAsk New Questionㅤ', style=discord.ButtonStyle.green, custom_id='qanda_submit_button', emoji=discord.PartialEmoji.from_str(Emoji.QANDA))
    async def ask_callback(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(QandaForm(self.client))

    async def interaction_check(self, interaction: discord.Interaction):
        return await checks(
            interaction,
            [is_ban_handler, is_inviter_handler]
        )


class QandaForm(discord.ui.Modal):
    def __init__(self, client: discord.Client):
        self.client = client

        super().__init__(
            title="Enter new question",
            custom_id="qanda_modal",
            timeout=200
        )

        self.add_item(
            TextInput(
                style= discord.TextStyle.short,
                label='❔ Title',
                placeholder="What's your gaming question? Be specific",
                custom_id='qanda_title_input',
                min_length = 5,
                max_length = 100,
                required = True,
            )
        )
        self.add_item(
            TextInput(
                style= discord.TextStyle.short,
                label='🕹️ Game',
                placeholder='Enter your game here...(optional)',
                custom_id='qanda_game_input',
                min_length = 5,
                max_length = 100,
                required = False,
            )
        )
        self.add_item(
            TextInput(
                style= discord.TextStyle.long,
                label='📝 Describe (Markdown supported)',
                placeholder='Enter your question description here...',
                custom_id='qanda_describe_input',
                min_length = 10,
                max_length = 650,
                required = True,
            )
        )
        self.add_item(
            TextInput(
                style= discord.TextStyle.short,
                label='📷 Media URL',
                placeholder='Enter your problem image URL here...(optional)',
                custom_id='qanda_media_input',
                min_length = 3,
                max_length = 200,
                required = False,
            )
        )
    
    async def on_submit(self, interaction: discord.Interaction):
        title = discord.utils.get(self.children, custom_id='qanda_title_input').value
        game_child = discord.utils.find(lambda c: c.custom_id == 'qanda_game_input', self.children)
        media_child = discord.utils.find(lambda c: c.custom_id == 'qanda_media_input', self.children)
        game = game_child.value if game_child else None
        media_url = await is_media(media_child.value) if media_child else None
        description = discord.utils.get(self.children, custom_id='qanda_describe_input').value

        qanda_channel = await interaction.guild.fetch_channel(Channel.QA_CHANNEL)

        em = discord.Embed(
            title=f'{Emoji.CIRCLE} {title.strip()}',
            description=f'\u200b\n_{description.strip()}_\n',
            colour=discord.Colour.yellow(),
            timestamp=datetime.now()
        )
        em.set_author(name='New Question!', icon_url=interaction.user.avatar.url)
        if game:
            em.add_field(name=f'\u200b', value=f'```🕹️ {game}```\n\u200b')
        if media_url:
            em.set_image(url=media_url)
        em.set_footer(text=f'Asked by {interaction.user.name}')
        question = await qanda_channel.send(embed=em, view=QandaView(self.client))

        thread = await question.create_thread(
            name='🚩 Answers'
        )
        await thread.edit(
            slowmode_delay=5
        )

        questioner = await MemberModel.find_one(MemberModel.member_id == interaction.user.id)
        qanda_model = QandaModel(
            title=title,
            question=description,
            search_query=f'{title} {description}',
            game=game,
            media=media_url,
            questioner=questioner,
            thread_id=thread.id,
            question_message_id=question.id,
        )
        await qanda_model.save()
        await questioner.update(
            Inc({MemberModel.question_asked_count: 1})
        )
        await interaction.response.send_message(
            embed=success_embed('Question created!'), 
            ephemeral=True
        )
