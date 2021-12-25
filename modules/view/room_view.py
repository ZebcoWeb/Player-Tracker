import discord

from discord import ButtonStyle, Client, Colour
from discord.interactions import Interaction
from discord.ui import view

from .view import PersistentView
from modules.database import MemberModel, RoomModel, GameModel
from modules.utils import i18n

from data.config import Emoji, Role, Category, Config


__all__ = ['CreateRoomView']

class CreateRoomView(PersistentView):

    @discord.ui.button(label='Create Room', custom_id='create_room_button', style=ButtonStyle.green, emoji=Emoji.CREATE_CIRCLE_TONE)
    async def choose_lang(self, button: discord.ui.Button, interaction: discord.Interaction):

        new_room_category: discord.CategoryChannel = self.client.get_channel(Category.NEW_ROOM)
        user = interaction.user
        guild = interaction.guild
        ram_role = guild.get_role(Role.RAM)
        member_model = MemberModel.objects.get(member_id=user.id)

        if new_room_category:
            channel_name = 'new-' + user.name.lower()
            
            overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
            ram_role: discord.PermissionOverwrite(read_messages=True, send_messages=False, manage_messages=True),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=False)
            }

            channel = await new_room_category.create_text_channel(
                name = channel_name,
                overwrites = overwrites,
                nsfw=False,
                reason = f'Creating a new room channel by {user.name.lower()}'
            )

            if member_model.lang:
                locate = i18n('room', member_model.lang.lower()) 
            else:
                locate = i18n('room', 'en') # default is 'en'
            locate.install()
            _ = locate.gettext

            em = discord.Embed(
                description=_(f'CONTEXT_CHOOSE_ROOM_LANG_DES\n\n{Emoji.TEST}'),
                color = Colour.green()
            )

            room_model = RoomModel(
                    creator = member_model,
                    status = 'process',
            )
            form = await channel.send(
                content=user.mention,
                embed=em,
                view=CreateRoomChooseLang(room_model, self.client)
            )
            view = discord.ui.View()
            button = discord.ui.Button(
                label='Click here',
                url= f'discord://-/channels/{form.guild.id}/{channel.id}/{form.id}',
            )
            view.add_item(button)

            await interaction.response.send_message(
                content = f'Navigate to the form to create a new room :',
                ephemeral = True,
                view=view
            )


class CreateRoomChooseLang(discord.ui.View):
    def __init__(self, room_model: RoomModel, client: Client):
        super().__init__(timeout=None)
        self.room_model: RoomModel = room_model
        self.client: Client = client

    
    async def on_timeout():
        print('timeout!')

    options = []
    for key, name, emoji in Config.LANGS:
        options.append(
            discord.SelectOption(
                label=name,
                value=key,
                emoji=emoji,
            )
        )

    @discord.ui.select(placeholder='Choose your room speaking language...', custom_id='choose_langs_select', options = options)
    async def choose_lang(self, select: discord.ui.Select, interaction: discord.Interaction):
        
        
        self.lang = select.values[0]
        self.room_model.lang = self.lang

        next_button: discord.ui.Button = discord.utils.get(
            self.children, custom_id='choose_next_lang_button'
        )

        next_button.disabled = False
        
        for set_default in select.options:
            if set_default.value == self.lang:
                set_default.default = True
            else:
                set_default.default = False

        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='Next', custom_id='choose_next_lang_button',disabled=True ,style=ButtonStyle.green, emoji=Emoji.ARROW_FORWARD)
    async def choose_lang_next(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.lang:
            em = discord.Embed(
                description='CONTEXT_CHOOSE_ROOM_GAME_DES',
                color = Colour.green()
            )
            em.set_author(name='CONTEXT_CHOOSE_ROOM_LANG_HEADER')
            em.set_footer(text='◇──◈──◇──◇──◇──◇')

            view = CreateRoomChooseGame(self.client, self.room_model)

            await interaction.response.edit_message(
                embed = em,
                view = view
            )





class CreateRoomChooseGame(discord.ui.View):
    def __init__(self, client, room_model):

        self.room_model: RoomModel = room_model
        self.client: Client = client

        super().__init__(timeout=None)

        self.add_item(GamesListSelectMenu(self.client))
        self.add_item(CreateRoomChooseGameNext())

    # @discord.ui.button(label='Next', custom_id='choose_next_game_button', disabled=True, style=ButtonStyle.green, emoji=Emoji.ARROW_FORWARD)
    # async def choose_game_next(self, button: discord.ui.Button, interaction: discord.Interaction):

    #     data = discord.utils.get(
    #         self.children, custom_id='choose_games_select'
    #     )
    #     game = data.values[0]

    #     if game not in ['next_page', 'previous_page']:

    #         self.room_model.game = GameModel.objects.get(id=game)

    #         em = discord.Embed(
    #             description='CONTEXT_CHOOSE_ROOM_GAME_DES',
    #             color = Colour.green()
    #         )
    #         em.set_author(name='CONTEXT_CHOOSE_ROOM_GAME_HEADER')
    #         em.set_footer(text='◇──◇──◇──◇──◇──◇')

            # view = CreateRoomChooseName(self.client, self.room_model)

            # await interaction.response.edit_message(
            #     embed = em,
            #     view = view
            # )

class CreateRoomChooseGameNext(discord.ui.Button):
    def __init__(self):
        super().__init__(label='Next', custom_id='choose_next_game_button', 
        disabled=True, style=ButtonStyle.green, emoji=Emoji.ARROW_FORWARD
    )

    async def callback(self, button: discord.ui.Button, interaction: discord.Interaction):

        data = discord.utils.get(
            self.view.children, custom_id='choose_games_select'
        )
        game = data.values[0]

        if game not in ['next_page', 'previous_page']:

            self.view.room_model.game = GameModel.objects.get(id=game)

            em = discord.Embed(
                description='CONTEXT_CHOOSE_ROOM_GAME_DES',
                color = Colour.green()
            )
            em.set_author(name='CONTEXT_CHOOSE_ROOM_GAME_HEADER')
            em.set_footer(text='◇──◇──◇──◇──◇──◇')

            # view = CreateRoomChooseName(self.client, self.room_model)

            # await interaction.response.edit_message(
            #     embed = em,
            #     view = view
            # )


class GamesListSelectMenu(discord.ui.Select):
    def __init__(self, client) -> None:
        self.client: Client = client
        self.option_coll = self._create_options()
        self.page_num = 0
        
        super().__init__(
            custom_id = 'choose_games_select', 
            placeholder = self._set_placeholder(), 
            options = self._pointer()
        )

    def _set_placeholder(self):
        return f'Choose your room game (Page {self.page_num + 1})'

    def _pointer(self):
        return self.option_coll[self.page_num]

    def next_page(self):
        self.page_num += 1
        self.options = self._pointer()
        self.placeholder = self._set_placeholder()

    def previous_page(self):
        self.page_num -= 1
        self.options = self._pointer()
        self.placeholder = self._set_placeholder()

    def _create_options(self):
        options_collection = []
        options = []
        for game in self.client.games:
            options.append(
                discord.SelectOption(
                    label = game.name_key,
                    description = '> 0 Playing now',
                    value = str(game.pk),
                )
            )
            if len(options) == 23: # create a collection of 23 options
                options_collection.append(options)
                options = []

        options_collection.append(options)
        options = []

        if len(options_collection) > 1:
            return self._paging_coll(options_collection)
        return options_collection

    def _paging_coll(self, options_collection):
        len_coll = len(options_collection)
        counter = 1
        for coll in options_collection:
            if counter < len_coll:
                coll.append(
                    discord.SelectOption(
                        label = 'Next Page',
                        value = 'next_page',
                        emoji = Emoji.ARROW_FORWARD
                    )
                )
            if counter > 1:
                coll.append(
                    discord.SelectOption(
                        label = 'previous page',
                        value = 'previous_page',
                        emoji = Emoji.ARROW_BACK,
                    )
                )
            counter += 1
        
        return options_collection

    async def callback(self, interaction: discord.Interaction):

        custom_id = interaction.data['values'][0]
        view: CreateRoomChooseGame = self.view
        next_button: discord.ui.Button = discord.utils.get(
            view.children, custom_id='choose_next_game_button'
        )
        new_menu = self

        if custom_id == 'next_page':
            new_menu.next_page()
            view.remove_item(self)
            view.add_item(new_menu)
            next_button.disabled = True

            for set_default in self.options:
                    set_default.default = False

        elif custom_id == 'previous_page':
            new_menu.previous_page()
            view.remove_item(self)
            view.add_item(new_menu)
            next_button.disabled = True

            for set_default in self.options:
                set_default.default = False

        else:
            next_button.disabled = False

            for set_default in self.options:
                if set_default.value == custom_id and custom_id not in ['next_page', 'previous_page']:
                    set_default.default = True
                else:
                    set_default.default = False

        await interaction.response.edit_message(view=view)


class CreateRoomChooseCapacity:
    def __init__(self, client, room_model):

        self.room_model: RoomModel = room_model
        self.client: Client = client

        super().__init__(timeout=None)
    