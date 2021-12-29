import asyncio

import discord
from discord import ButtonStyle, Client, Colour

from data.config import Category, Config, Emoji, Role
from modules.database import GameModel, MemberModel, RoomModel
from modules.utils import i18n

from .view import PersistentView

__all__ = ['CreateRoomView']

class CreateRoomView(PersistentView):

    @discord.ui.button(label='Create Room', custom_id='create_room_button', style=ButtonStyle.green, emoji=Emoji.CREATE_CIRCLE_TONE)
    async def choose_lang(self, button: discord.ui.Button, interaction: discord.Interaction):

        new_room_category: discord.CategoryChannel = self.client.get_channel(Category.NEW_ROOM)
        user = interaction.user
        guild = interaction.guild
        ram_role = guild.get_role(Role.RAM)
        member_model = await MemberModel.find_one({'member_id': user.id})

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

            locate = i18n() # default is 'en'
            _ = locate.gettext

            em = discord.Embed(
                description=_(f'CONTEXT_CHOOSE_ROOM_LANG_DES\n\n{Emoji.TEST}'),
                color = Colour.green()
            )

            room_model = RoomModel(creator=member_model)

            room_model.room_create_channel_id = channel.id

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
                default=False
            )
        )

    @discord.ui.select(placeholder='Choose your room speaking language...', custom_id='choose_langs_select', options = options)
    async def choose_lang(self, select: discord.ui.Select, interaction: discord.Interaction):
        
        
        self.lang = select.values[0]

        next_button: discord.ui.Button = discord.utils.get(
            self.children, custom_id='choose_next_lang_button'
        )

        self.room_model.lang = self.lang # set lang

        next_button.disabled = False
        
        for set_default in select.options:
            if set_default.value == self.lang:
                set_default.default = True
            else:
                set_default.default = False

        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='ㅤNextㅤ', custom_id='choose_next_lang_button',disabled=True ,style=ButtonStyle.green, emoji=Emoji.ARROW_FORWARD)
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
                    value = str(game.id),
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


class CreateRoomChooseGameNext(discord.ui.Button):
    def __init__(self):
        super().__init__(label='ㅤNextㅤ', custom_id='choose_next_game_button', 
        disabled=True, style=ButtonStyle.green, emoji=Emoji.ARROW_FORWARD
    )

    async def callback(self, interaction: discord.Interaction):

        view = self.view

        data = discord.utils.get(
            view.children, custom_id='choose_games_select'
        )
        game = data.values[0]

        if game not in ['next_page', 'previous_page']:

            view.room_model.game = GameModel.get(game)
            view.room_model.start_msg_id = interaction.message.id

            em = discord.Embed(
                description='CONTEXT_CHOOSE_ROOM_CAPACITY_DES',
                color = Colour.green()
            )
            em.set_author(name='CONTEXT_CHOOSE_ROOM_CAPACITY_HEADER')
            em.set_footer(text='◇──◇──◇──◇──◇──◇')

            view = CreateRoomChooseCapacity(view.client, view.room_model)

            await interaction.response.edit_message(
                embed = em,
                view = view
            )


class CreateRoomChooseCapacity(discord.ui.View):
    def __init__(self, client, room_model):

        self.room_model: RoomModel = room_model
        self.client: Client = client

        super().__init__(timeout=None)
    

        counter = 1
        for i in Config.ROOM_CAPACITIES:

            button = discord.ui.Button(
                style=ButtonStyle.gray,
                custom_id = i,
                emoji = self.client.get_emoji(Config.ROOM_CAPACITIES.get(i).get('emoji')),
                row=0
            )
            if counter > 4: # create a new row
                button.row += 1
    
            counter += 1

            button.callback = self.callback
            self.add_item(button)
    
    async def callback(self, interaction: discord.Interaction):
            
        value = interaction.data.get('custom_id')
        capacity = Config.ROOM_CAPACITIES.get(value).get('capacity')

        self.room_model.capacity = capacity

        em = discord.Embed(
            description='CONTEXT_CHOOSE_ROOM_BITRATE_DES',
            color = Colour.green()
        )
        em.set_author(name='CONTEXT_CHOOSE_ROOM_BITRATE_HEADER')
        em.set_footer(text='◇──◇──◇──◇──◇──◇')

        view = CreateRoomChooseBitrate(self.client, self.room_model)

        await interaction.response.edit_message(
            embed = em,
            view = view
        )

# TODO: add region
# TODO: is waiting room
class CreateRoomChooseBitrate(discord.ui.View):
    def __init__(self, client, room_model):

        self.room_model: RoomModel = room_model
        self.client: Client = client

        super().__init__(timeout=None)
    
        for i in Config.ROOM_BITRATES:
            
            button = discord.ui.Button(
                style=ButtonStyle.gray,
                label = 'kb',
                custom_id = i,
                emoji = self.client.get_emoji(Config.ROOM_BITRATES.get(i).get('emoji')),
            )

            button.callback = self.callback
            self.add_item(button)
    
    async def callback(self, interaction: discord.Interaction):

        value = interaction.data.get('custom_id')
        bitrate = Config.ROOM_BITRATES.get(value).get('bitrate')

        self.room_model.bitrate = bitrate
        em = discord.Embed(
            description='CONTEXT_CHOOSE_ROOM_MODE_DES',
            color = Colour.green()
        )
        em.set_author(name='CONTEXT_CHOOSE_ROOM_MODE_HEADER')
        em.set_footer(text='◇──◇──◇──◇──◇──◇')

        view = CreateRoomChooseMode(self.client, self.room_model)

        await interaction.response.edit_message(
            embed = em,
            view = view
        )
class CreateRoomChooseMode(discord.ui.View):
    def __init__(self, client, room_model):

        self.room_model: RoomModel = room_model
        self.client: Client = client

        super().__init__(timeout=None)
    
        for i in Config.ROOM_MODES:
            
            button = discord.ui.Button(
                style=Config.ROOM_MODES.get(i).get('style'),
                label = Config.ROOM_MODES.get(i).get('i18n'),
                custom_id = i,
                emoji = self.client.get_emoji(Config.ROOM_MODES.get(i).get('emoji')),
            )

            button.callback = self.callback
            self.add_item(button)
    
    async def callback(self, interaction: discord.Interaction):

        value = interaction.data.get('custom_id')
        mode = Config.ROOM_MODES.get(value).get('mode')

        self.room_model.mode = mode
        print(self.room_model.__dict__)
        em = discord.Embed(
            description='CONTEXT_CHOOSE_ROOM_CONFIRM_DES',
            color = Colour.green()
        )
        em.set_author(name='CONTEXT_CHOOSE_ROOM_CONFIRM_HEADER')
        em.set_footer(text='◇──◇──◇──◇──◇──◇')

        view = CreateRoomConfirm(self.client, self.room_model)

        await interaction.response.edit_message(
            embed = em,
            view = view
        )

class CreateRoomConfirm(discord.ui.View):
    def __init__(self, client, room_model):

        self.room_model: RoomModel = room_model
        self.client: Client = client

        super().__init__(timeout=None)

        self.add_item(RoomConfirmButton(
            emoji=self.client.get_emoji(Emoji.CONFIRM_TONE_ID),
        ))

        self.add_item(RoomAgainButton(
            emoji=self.client.get_emoji(Emoji.AGAIN_TONE_ID),
        ))

        self.add_item(RoomCancelButton(
            emoji=self.client.get_emoji(Emoji.CABCEL_TONE_ID),
        ))


class RoomConfirmButton(discord.ui.Button):
    def __init__(self, emoji: Emoji):
        super().__init__(
            label='Confirm',
            custom_id='confirm_button',
            style=ButtonStyle.green,
            emoji=emoji,
        )

    async def callback(self, interaction: discord.Interaction):
        pass

class RoomAgainButton(discord.ui.Button):
    def __init__(self, emoji: Emoji):
        super().__init__(
            label='Again',
            custom_id='again_button',
            style=ButtonStyle.blurple,
            emoji=emoji,
        )

    async def callback(self, interaction: discord.Interaction):

        room_model: RoomModel = self.view.room_model
        client = self.view.client
        new_room_model = RoomModel(
            creator = room_model.creator,
            start_msg_id = room_model.start_msg_id,
            room_create_channel_id = room_model.room_create_channel_id,
            room_again_created = True
        )
        
        del room_model
        
        locate = i18n() # default is 'en'
        _ = locate.gettext

        em = discord.Embed(
                description=_(f'CONTEXT_CHOOSE_ROOM_LANG_DES\n\n{Emoji.TEST}'),
                color = Colour.green()
        )
        em.set_footer(text='◇──◈──◇──◇──◇──◇')

        view = CreateRoomChooseLang(client, new_room_model)

        await interaction.response.edit_message(
            embed = em,
            view = view
        )

class RoomCancelButton(discord.ui.Button):
    def __init__(self, emoji: Emoji):
        super().__init__(
            label='Cancel',
            custom_id='cancel_button',
            style=ButtonStyle.red,
            emoji=emoji,
        )

    async def callback(self, interaction: discord.Interaction):
        em = discord.Embed(
            description='CANCEL_ROOM_DES',
            color = Colour.red()
        )
        em.set_author(name='CANCEL_ROOM_HEADER')

        await interaction.response.edit_message(
            embed=em, 
            view=RoomCloseCancelView(self.view.client, self.view.room_model)
        )

class RoomCloseCancelView(discord.ui.View):
    def __init__(self, client, room_model):

        self.room_model: RoomModel = room_model
        self.client: Client = client

        super().__init__(timeout=None)

        button_yes = discord.ui.Button(
                label= 'ㅤㅤㅤYESㅤㅤㅤ',
                style=ButtonStyle.green,
                custom_id='close_room_yes',
        )
        button_yes.callback = self.callback_yes

        button_no = discord.ui.Button(
                label= 'NO',
                style=ButtonStyle.red,
                custom_id='close_room_no',

        )
        button_no.callback = self.callback_no
        

        self.add_item(button_yes)
        self.add_item(button_no)

    async def callback_yes(self, interaction: discord.Interaction):
        em = discord.Embed(
            description='CLOSE_ROOM_DES',
            color = Colour.red()
        )
        em.set_author(name='CLOSE_ROOM_HEADER')

        await interaction.response.edit_message(embed=em, view=None)
        channel = await self.client.fetch_channel(self.room_model.room_create_channel_id)
        
        await asyncio.sleep(10)

        await channel.delete()
        del self.room_model

    async def callback_no(self, interaction: discord.Interaction):
        pass