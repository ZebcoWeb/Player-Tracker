import discord

from datetime import datetime
from discord.ui import InputText, Button

from data.config import Channel, Emoji
from modules.database.models import QandaModel, MemberModel
from modules.utils import is_ban

from .view import PersistentView


class QandaView(PersistentView):
    def __init__(self, client: discord.Client):
        self.client = client
        super().__init__(timeout=None)

        button = Button(
            label='ㅤAsk Questionㅤ', 
            style=discord.ButtonStyle.green, 
            custom_id='qanda_submit_button',
            emoji=self.client.get_emoji(Emoji.QA_ID)
        )
        self.add_item(button)
        button.callback = self.submit_button

    # @is_ban #Todo: fix that
    async def submit_button(self, interaction: discord.Interaction):
        await interaction.response.send_modal(QandaForm(self.client))


class QandaForm(discord.ui.Modal):
    def __init__(self, client: discord.Client):
        self.client = client
        super().__init__(
            title="Enter new question",
            custom_id="qanda_modal"
        )

        self.add_item(
            InputText(
                style= discord.InputTextStyle.short,
                label='Title',
                placeholder="What's your gaming question? Be specific",
                custom_id='qanda_title_input',
                min_length = 5,
                max_length = 60,
                required = True,
            )
        )
        self.add_item(
            InputText(
                style= discord.InputTextStyle.short,
                label='Game',
                placeholder='Enter your game here...(optional)',
                custom_id='qanda_game_input',
                min_length = 5,
                max_length = 100,
                required = False,
            )
        )
        self.add_item(
            InputText(
                style= discord.InputTextStyle.long,
                label='Describe',
                placeholder='Enter your question description here...',
                custom_id='qanda_describe_input',
                min_length = 10,
                max_length = 350,
                required = True,
            )
        )
    
    async def callback(self, interaction: discord.Interaction):
        title = discord.utils.get(self.children, custom_id='qanda_title_input').value
        game_child = discord.utils.find(lambda c: c.custom_id == 'qanda_game_input', self.children)
        game = game_child.value if game_child else None
        description = discord.utils.get(self.children, custom_id='qanda_describe_input').value

        qanda_channel = await interaction.guild.fetch_channel(Channel.QA_CHANNEL)

        em = discord.Embed(
            title=f'{Emoji.CIRCLE} {title}',
            description=f'\u200b\n_{description}_\n',
            colour=discord.Colour.yellow(),
            timestamp=datetime.now()
        )
        em.set_author(name='New Question!', icon_url=interaction.user.avatar.url)
        if game:
            em.add_field(name=f'\u200b', value=f'`🕹️` **{game}**\n\u200b')
        em.set_footer(text=f'Created by {interaction.user.name}')
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
            game=game if game else None,
            questioner=questioner,
            thread_id=thread.id,
            question_message_id=question.id,
        )
        await qanda_model.save()
        await interaction.response.send_message(f'Question created!', ephemeral=True)