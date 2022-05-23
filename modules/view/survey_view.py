import discord

from modules.database import SurveyModel, SectionEnum, UXEnum, SupportEnum, MemberModel
from data.config import Config, Emoji, Vote
from modules.utils import set_level

from .view import PersistentView



__all__ = ['StartSurveyView']

class StartSurveyView(PersistentView):

    @discord.ui.button(label='ㅤㅤㅤㅤㅤㅤㅤㅤStart Survayㅤㅤㅤㅤㅤㅤㅤㅤ', style=discord.ButtonStyle.green, custom_id='start_survey_button')
    async def callback(self, interaction: discord.Interaction, button: discord.ui.Button):

        member_model = await MemberModel.find_one(MemberModel.member_id == interaction.user.id)
        survey_model = SurveyModel(
            target_user=member_model,
            channel_id=interaction.channel.id,
        )
        em = discord.Embed(
            title='🤔 How about your experience with this platform so far?',
            description='ㅤ\n\n' + set_level(2),
            color=Config.BRAND_COLOR
        )
        await interaction.response.edit_message(embed=em, view=UXView(survey_model))

class UXView(discord.ui.View):
    def __init__(self, survey_model: SurveyModel):
        super().__init__(timeout=None)
        self.survey_model = survey_model

        item_1 = discord.ui.Button(label='Excellent!', style=discord.ButtonStyle.green, custom_id='ux_excellent_button', emoji=discord.PartialEmoji.from_str(Emoji.EXCELLENT))
        item_2 = discord.ui.Button(label='Good', style=discord.ButtonStyle.blurple, custom_id='ux_good_button', emoji=discord.PartialEmoji.from_str(Emoji.GOOD))
        item_3 = discord.ui.Button(label='Bad', style=discord.ButtonStyle.red, custom_id='ux_bad_button', emoji=discord.PartialEmoji.from_str(Emoji.BAD))
        item_1.callback = self.callback
        item_2.callback = self.callback
        item_3.callback = self.callback
        self.add_item(item_1)
        self.add_item(item_2)
        self.add_item(item_3)


    async def callback(self, interaction: discord.Interaction):
        custom_id = interaction.data['custom_id']

        if custom_id == 'ux_excellent_button':
            self.survey_model.ux_choice = UXEnum.excellent
        elif custom_id == 'ux_good_button':
            self.survey_model.ux_choice = UXEnum.good
        elif custom_id == 'ux_bad_button':
            self.survey_model.ux_choice = UXEnum.bad

        em = discord.Embed(
            title='🤔 Which section did you use the most?',
            description='ㅤ\n\n' + set_level(3),
            color=Config.BRAND_COLOR
        )
        await interaction.response.edit_message(embed=em, view=SectionView(self.survey_model))

class SectionView(discord.ui.View):
    def __init__(self, survey_model: SurveyModel):
        super().__init__(timeout=None)
        self.survey_model = survey_model

        item_1 = discord.ui.Button(label=SectionEnum.room, style=discord.ButtonStyle.blurple, custom_id='room_button')
        item_2 = discord.ui.Button(label=SectionEnum.qanda, style=discord.ButtonStyle.blurple, custom_id='qanda_button')
        item_3 = discord.ui.Button(label=SectionEnum.other, style=discord.ButtonStyle.blurple, custom_id='other_button')
        item_1.callback = self.callback
        item_2.callback = self.callback
        item_3.callback = self.callback
        self.add_item(item_1)
        self.add_item(item_2)
        self.add_item(item_3)


    async def callback(self, interaction: discord.Interaction):
        custom_id = interaction.data['custom_id']

        if custom_id == 'room_button':
            self.survey_model.section_choice = SectionEnum.room
        elif custom_id == 'qanda_button':
            self.survey_model.section_choice = SectionEnum.qanda
        elif custom_id == 'other_button':
            self.survey_model.section_choice = SectionEnum.other
    
        em = discord.Embed(
            title='🤔 What was the performance level of the support team?',
            description='ㅤ\n\n' + set_level(4),
            color=Config.BRAND_COLOR
        )
        await interaction.response.edit_message(embed=em, view=SupportView(self.survey_model))


class SupportView(discord.ui.View):
    def __init__(self, survey_model: SurveyModel):
        super().__init__(timeout=None)
        self.survey_model = survey_model

        item_1 = discord.ui.Button(label='ㅤㅤStrongㅤㅤ', style=discord.ButtonStyle.blurple, custom_id='strong_button')
        item_2 = discord.ui.Button(label='ㅤㅤPoorㅤㅤ', style=discord.ButtonStyle.red, custom_id='poor_button')
        item_1.callback = self.callback
        item_2.callback = self.callback
        self.add_item(item_1)
        self.add_item(item_2)


    async def callback(self, interaction: discord.Interaction):
        custom_id = interaction.data['custom_id']

        if custom_id == 'strong_button':
            self.survey_model.support_choice = SupportEnum.strong
        elif custom_id == 'poor_button':
            self.survey_model.support_choice = SupportEnum.poor
        
        em = discord.Embed(
            title='🤔 Do you have a new idea or suggestion? We are eager to read it',
            description='ㅤ\n\n' + set_level(5, True),
            color=Config.BRAND_COLOR
        )
        await interaction.response.edit_message(embed=em, view=SuggestionView(self.survey_model))


class SuggestModal(discord.ui.Modal):
    def __init__(self, survey_model: SurveyModel, view: discord.ui.View) -> None:
        super().__init__(title='Enter your suggestion', timeout=None)
        self.survey_model = survey_model
        self.view = view

        self.add_item(
            discord.ui.TextInput(
                label='💡 Suggestion',
                style=discord.TextStyle.long,
                placeholder='Enter your suggestion here',
                custom_id='suggestion_input',
                required=True,
                min_length=5,
                max_length=1000
            )
        )

    async def on_submit(self, interaction: discord.Interaction):
        self.survey_model.suggestion = discord.utils.get(self.children, custom_id='suggestion_input').value
        await self.survey_model.save()
        await self.view.next_view(interaction)


class SuggestionView(discord.ui.View):
    def __init__(self, survey_model: SurveyModel):
        super().__init__(timeout=None)
        self.survey_model = survey_model
    
    async def next_view(self, interaction: discord.Interaction):
        em = discord.Embed(
            title='Thanks for taking your time',
            description= '⚡ If you are interested in helping us make the community bigger and more visible, you can make a valuable contribution by voting and commenting on the following websites. \n\n- ***More population, more facilities***',
            color=Config.BRAND_COLOR
        )
        await interaction.response.edit_message(embed=em, view=ServerVoteView())


    @discord.ui.button(label='ㅤㅤSubmitㅤㅤ', style=discord.ButtonStyle.green, custom_id='submit_button')
    async def callback_suggest(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SuggestModal(self.survey_model, self))


    @discord.ui.button(label='Pass', style=discord.ButtonStyle.blurple, custom_id='pass_button')
    async def callback_pass(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.survey_model.suggestion = None
        await self.survey_model.save()
        await self.next_view(interaction)
    


class ServerVoteView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
        self.add_item(
            discord.ui.Button(
                emoji=discord.PartialEmoji.from_str(Vote.TOPGG_EMOJI),
                url=Vote.TOPGG
            )
        )
        self.add_item(
            discord.ui.Button(
                emoji=discord.PartialEmoji.from_str(Vote.DISBOARD_EMOJI),
                url=Vote.DISBOARD
            )
        )
        self.add_item(
            discord.ui.Button(
                emoji=discord.PartialEmoji.from_str(Vote.DISCORD_SERVERS_EMOJI),
                url=Vote.DISCORD_SERVERS
            )
        )
        self.add_item(
            discord.ui.Button(
                emoji=discord.PartialEmoji.from_str(Vote.DISCORD_ST_EMOJI),
                url=Vote.DISCORD_ST
            )
        )

        close_button = discord.ui.Button(label='Close', style=discord.ButtonStyle.red, custom_id='close_button')
        close_button.callback = self.callback
        self.add_item(close_button)

    async def callback(self, interaction: discord.Interaction):
        await interaction.channel.delete()
