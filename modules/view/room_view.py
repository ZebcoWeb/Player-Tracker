import asyncio
import random
import discord

from io import BytesIO
from PIL import Image
from discord import ButtonStyle, Client, Colour
from beanie.odm.operators.update.general import Set, Inc

import data.contexts as C
from data.config import Category, Channel, Config, Emoji, Role
from modules.database import GameModel, MemberModel, RoomModel
from modules.database.models.languages import LangModel
from modules.utils import (
small_letter, set_level, had_room_handler, 
success_embed, error_embed, is_ban_handler, 
is_inviter_handler, checks, capacity_humanize,
tracker_message_players, generate_tracker_footer,
)
from .view import PersistentView
from .room_user_panel import RoomUserPanel
from .like_view import LikeButton

__all__ = ['CreateRoomView', 'RoomPlayerCountButton', 'RoomSendInvite']


class RoomSendInvite(discord.ui.View):
    def __init__(self, client: Client, room_model: RoomModel):
        self.client = client
        self.room_model = room_model
        super().__init__(timeout=None)


    @discord.ui.button(label='ㅤㅤAcceptㅤㅤ', style=ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc_room = await self.client.fetch_channel(self.room_model.room_voice_channel_id)
        overwrites = vc_room.overwrites
        overwrites[interaction.user] = discord.PermissionOverwrite(connect=True, view_channel=True)
        await vc_room.edit(overwrites=overwrites)
        em = discord.Embed(
            description=f'{Emoji.ARROW_FORWARD} Your invite URL: {self.room_model.invite_url}',
            colour=Colour.green()
        )
        await interaction.response.send_message(embed=em)
        
        room_text_channel = await self.client.fetch_channel(self.room_model.room_create_channel_id)
        await room_text_channel.send(
            content=f'<@{self.room_model.creator.member_id}>',
            embed=success_embed(f'{interaction.user.mention} accepted your invite.')
        )
    
    @discord.ui.button(label='ㅤRejectㅤ', style=ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.edit(
            view=None
        )
        await interaction.response.send_message(
            embed=success_embed(f'Your invite has been rejected.')
        )

        room_text_channel = await self.client.fetch_channel(self.room_model.room_create_channel_id)
        await room_text_channel.send(
            content=f'<@{self.room_model.creator.member_id}>',
            embed=error_embed(f'{interaction.user.mention} rejected your invite.')
        )


class RoomPlayerCountButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label='0 Players',
            style = ButtonStyle.blurple,
            custom_id='player_count_button',
            emoji=discord.PartialEmoji.from_str(Emoji.USERS)
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

class CreateRoomView(PersistentView):

    @discord.ui.button(label='ㅤCreate Roomㅤ', custom_id='create_room_button', style=ButtonStyle.green, emoji=Emoji.CREATE_CIRCLE)
    async def choose_lang(self, interaction: discord.Interaction, button: discord.ui.Button):

        new_room_category: discord.CategoryChannel = self.client.get_channel(Category.PLATFORM)
        user = interaction.user
        guild = interaction.guild
        ram_role = guild.get_role(Role.RAM)
        member_model = await MemberModel.find_one({'member_id': user.id})

        if new_room_category:
            channel_name = 'room-' + user.name.lower()
            
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
                reason = f'Creating a new room channel by {user.name.lower()}',
                position=1
            )

            em = discord.Embed(
                description = C.CONTEXT_LANG['des'] % (await LangModel.count()),
                color = Colour.green()
            )
            em.set_author(name=C.CONTEXT_LANG['title'])
            em.description += '\n\n' + set_level(1)

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
    
    async def interaction_check(self, interaction: discord.Interaction):
        return await checks(
            interaction,
            [is_inviter_handler, is_ban_handler, had_room_handler]
        )


class CreateRoomChooseLang(discord.ui.View):
    def __init__(self, room_model: RoomModel, client: Client):
        super().__init__(timeout=Config.ROOM_CREATION_TIMEOUT)
        self.room_model: RoomModel = room_model
        self.client: Client = client
        self.is_done = False
        self.select = discord.ui.Select(
            placeholder= 'Choose your room speaking language',
            custom_id='choose_langs_select',
            options=self._load_options(),
        )
        self.select.callback = self.choose_lang

        next_button = discord.ui.Button(
            label='ㅤNextㅤ',
            custom_id='choose_next_lang_button',
            disabled=True,
            style=ButtonStyle.green, 
            emoji=Emoji.ARROW_FORWARD,
        )
        next_button.callback = self.choose_lang_next

        self.add_item(self.select)
        self.add_item(next_button)

    def _load_options(self):
        options = []
        for lang in self.client.langs:
            options.append(
                discord.SelectOption(
                    label=lang.name,
                    value=lang.name,
                    default=False
                )
            )
        return options

    async def choose_lang(self, interaction: discord.Interaction):
        
        self.lang = interaction.data['values'][0]

        next_button: discord.ui.Button = discord.utils.get(
            self.children, custom_id='choose_next_lang_button'
        )

        self.room_model.lang = discord.utils.get(self.client.langs, name=self.lang)

        next_button.disabled = False
        
        for set_default in self.select.options:
            if set_default.value == self.lang:
                set_default.default = True

            else:
                set_default.default = False

        await interaction.response.edit_message(view=self)
    
    async def choose_lang_next(self, interaction: discord.Interaction):
        if self.lang:
            self.is_done = True
            em = discord.Embed(
                description= C.CONTEXT_GAME['des'] % (len(self.client.games)),
                color = Colour.green()
            )
            em.description += '\n\n' + set_level(2)
            em.set_author(name=C.CONTEXT_GAME['title'])

            view = CreateRoomChooseGame(self.client, self.room_model)

            await interaction.response.edit_message(
                embed = em,
                view = view
            )
    
    async def on_timeout(self):
        if not self.is_done:
            room_channel = await self.client.fetch_channel(self.room_model.room_create_channel_id)
            await room_channel.delete(reason='Room creation timeout')


class CreateRoomChooseGame(discord.ui.View):
    def __init__(self, client, room_model):
        self.room_model: RoomModel = room_model
        self.client: Client = client
        self.is_done = False

        super().__init__(timeout=Config.ROOM_CREATION_TIMEOUT)

        self.add_item(GamesListSelectMenu(self.client))
        self.add_item(CreateRoomChooseGameNext())
    
    async def on_timeout(self):
        if not self.is_done:
            room_channel = await self.client.fetch_channel(self.room_model.room_create_channel_id)
            await room_channel.delete(reason='Room creation timeout')


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
                    emoji=game.get_emoji(self.client),
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
                        label = 'Previous page',
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
            view.is_done = True
            view.room_model.game = await GameModel.get(game)
            view.room_model.start_msg_id = interaction.message.id

            em = discord.Embed(
                description=C.CONTEXT_ROOM_LIMIT['des'],
                color = Colour.green()
            )
            em.description += '\n\n' + set_level(3)
            em.set_author(name=C.CONTEXT_ROOM_LIMIT['title'])

            view = CreateRoomChooseCapacity(view.client, view.room_model)

            await interaction.response.edit_message(
                embed = em,
                view = view
            )


class CreateRoomChooseCapacity(discord.ui.View):
    def __init__(self, client, room_model):
        self.room_model: RoomModel = room_model
        self.client: Client = client
        self.is_done = False

        super().__init__(timeout=Config.ROOM_CREATION_TIMEOUT)
    

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
        self.is_done = True
        value = interaction.data.get('custom_id')
        capacity = Config.ROOM_CAPACITIES.get(value).get('capacity')
        self.room_model.capacity = capacity

        em = discord.Embed(
            description=C.CONTEXT_ROOM_BITRATE['des'],
            color = Colour.green()
        )
        em.description += '\n\n' + set_level(4)
        em.set_author(name=C.CONTEXT_ROOM_BITRATE['title'])

        view = CreateRoomChooseBitrate(self.client, self.room_model)

        await interaction.response.edit_message(
            embed = em,
            view = view
        )
    
    async def on_timeout(self):
        if not self.is_done:
            room_channel = await self.client.fetch_channel(self.room_model.room_create_channel_id)
            await room_channel.delete(reason='Room creation timeout')

# TODO: is waiting room

class CreateRoomChooseBitrate(discord.ui.View):
    def __init__(self, client, room_model):
        self.room_model: RoomModel = room_model
        self.client: Client = client
        self.is_done = False

        super().__init__(timeout=Config.ROOM_CREATION_TIMEOUT)
    
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
        self.is_done = True
        value = interaction.data.get('custom_id')
        bitrate = Config.ROOM_BITRATES.get(value).get('bitrate')
        self.room_model.bitrate = bitrate

        em = discord.Embed(
            description=C.CONTEXT_ROOM_MODE['des'],
            color = Colour.green()
        )
        em.description += '\n\n' + set_level(5)
        em.set_author(name=C.CONTEXT_ROOM_MODE['title'])

        view = CreateRoomChooseMode(self.client, self.room_model)

        await interaction.response.edit_message(
            embed = em,
            view = view
        )

    async def on_timeout(self):
        if not self.is_done:
            room_channel = await self.client.fetch_channel(self.room_model.room_create_channel_id)
            await room_channel.delete(reason='Room creation timeout')
        
class CreateRoomChooseMode(discord.ui.View):
    def __init__(self, client, room_model):
        self.room_model: RoomModel = room_model
        self.client: Client = client
        self.is_done = False

        super().__init__(timeout=Config.ROOM_CREATION_TIMEOUT)
    
        for i in Config.ROOM_MODES:
            
            button = discord.ui.Button(
                style=Config.ROOM_MODES.get(i).get('style'),
                label = Config.ROOM_MODES.get(i).get('label'),
                custom_id = i,
                emoji = self.client.get_emoji(Config.ROOM_MODES.get(i).get('emoji')),
            )

            button.callback = self.callback
            self.add_item(button)
    
    async def callback(self, interaction: discord.Interaction):
        self.is_done = True
        value = interaction.data.get('custom_id')
        mode = Config.ROOM_MODES.get(value).get('mode')

        self.room_model.mode = mode

        em = discord.Embed(
            description=C.CONTEXT_CONFIRM_ROOM.get('des'),
            color = Colour.green()
        )
        em.description += '\n\n' + set_level(6, True)
        em.set_author(name=C.CONTEXT_CONFIRM_ROOM.get('title'))

        view = CreateRoomConfirm(self.client, self.room_model)

        await interaction.response.edit_message(
            embed = em,
            view = view
        )
    
    async def on_timeout(self):
        if not self.is_done:
            room_channel = await self.client.fetch_channel(self.room_model.room_create_channel_id)
            await room_channel.delete(reason='Room creation timeout')

class CreateRoomConfirm(discord.ui.View):
    def __init__(self, client, room_model):
        self.room_model: RoomModel = room_model
        self.client: Client = client
        self.is_done = False

        super().__init__(timeout=Config.ROOM_CREATION_TIMEOUT)

        self.add_item(RoomConfirmButton(emoji=self.client.get_emoji(Config.ROOM_CONFIRM.get('confirm_button').get('emoji'))))
        self.add_item(RoomAgainButton(emoji=self.client.get_emoji(Config.ROOM_CONFIRM.get('again_button').get('emoji'))))
        self.add_item(RoomCancelButton(emoji=self.client.get_emoji(Config.ROOM_CONFIRM.get('cancel_button').get('emoji'))))
    
    async def on_timeout(self):
        if not self.is_done:
            room_channel = await self.client.fetch_channel(self.room_model.room_create_channel_id)
            await room_channel.delete(reason='Room creation timeout')

class RoomConfirmButton(discord.ui.Button):
    def __init__(self, emoji: Emoji):
        super().__init__(
            label=Config.ROOM_CONFIRM.get('confirm_button').get('label'),
            custom_id=Config.ROOM_CONFIRM.get('confirm_button').get('id'),
            style=ButtonStyle.green,
            emoji=emoji,
        )

    async def callback(self, interaction: discord.Interaction):
        self.is_done = True
        room_model: RoomModel = self.view.room_model
        client: discord.Client = self.view.client
        guild = interaction.guild
        user = await guild.fetch_member(room_model.creator.member_id)
        ram_role = guild.get_role(Role.RAM)

        category_room: discord.CategoryChannel = await client.fetch_channel(Category.ROOMS)

        if room_model.mode == 'private':
            mode = False
        elif room_model.mode == 'public':
            mode = True

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=True, connect=mode, create_instant_invite=mode),
            guild.me: discord.PermissionOverwrite(manage_channels=True),
            ram_role: discord.PermissionOverwrite(manage_channels=False, manage_permissions=True, connect=True, deafen_members=True, mute_members=True, move_members=True),
            user: discord.PermissionOverwrite(view_channel=True, connect=True, deafen_members=True, mute_members=True, priority_speaker=True)
        }

        if room_model.capacity == 2:
            namespace = 'Due'
        elif room_model.capacity == 3:
            namespace = 'Trio'
        elif room_model.capacity == 4:
            namespace = 'Quad'
        else:
            namespace = 'Room'

        game_obj: GameModel = room_model.game

        room_name = f'{namespace} #{await RoomModel.count() + 1} .{small_letter(room_model.lang.short)} .{small_letter(game_obj.short)}'

        vc_room = await category_room.create_voice_channel(
            name = room_name,
            overwrites = overwrites,
            bitrate = room_model.bitrate,
            user_limit = room_model.capacity,
            position = 0,
            video_quality_mode = discord.VideoQualityMode.auto
        )
        room_model.room_voice_channel_id = vc_room.id

        if room_model.mode == 'public':
            invite = await vc_room.create_invite()
            
            room_model.invite_url = invite.url
            room_model.tracker_channel_id = random.choice(Channel.TRACKER_CHANNELS)
            tracker_channel = client.get_channel(room_model.tracker_channel_id)

            emt_description = tracker_message_players(0, room_model.capacity)

            random_color = discord.Colour.random()
            emt = discord.Embed(
                description=emt_description,
                color=random_color,
            )
            emt.set_author(name=f'New room created by {user.display_name}#{user.discriminator}', icon_url=user.display_avatar.url)
            emt.set_thumbnail(url=room_model.game.logo_url)
            emt.add_field(name='🌍  Language', value=f'ㅤ**⤷** *{room_model.lang.name}*', inline=True)
            emt.add_field(name='🕹️  Game', value=f'ㅤ**⤷** *{room_model.game.name_key}*', inline=True)
            emt.add_field(name='👨‍💻  Capacity', value=f'ㅤ**⤷** *{capacity_humanize(room_model.capacity)}*', inline=True)

            emt.set_image(
                url=await generate_tracker_footer(client, random_color)
            )

            join_button = discord.ui.Button(
                label='Join Now',
                url=invite.url,
            )
            tracker_view = discord.ui.View(timeout=None)
            tracker_view.add_item(join_button)
            tracker_view.add_item(LikeButton())

            tracker_msg = await tracker_channel.send(
                embed=emt,
                view=tracker_view
            )

            room_model.tracker_msg_id = tracker_msg.id

        elif room_model.mode == 'private':

            max_uses = lambda x: 0 if x is None else x

            invite = await vc_room.create_invite(
                max_uses=max_uses(room_model.capacity),
                max_age=0,
            )

            room_model.invite_url = invite.url

        
        await room_model.save() #! fix signal & delete role

        await MemberModel.find_one(MemberModel.member_id == room_model.creator.member_id).update(
            Inc({MemberModel.room_create_value: 1}),
            Set({MemberModel.latest_game_played: room_model.game}),
            Set({MemberModel.lang: room_model.lang}),
        )

        if room_model.mode == 'public':
            embed_des = C.CONTEXT_CREATED_ROOM.get('public_des') % (room_model.tracker_channel_id, room_model.room_voice_channel_id, room_model.invite_url)
        else:
            embed_des = C.CONTEXT_CREATED_ROOM.get('private_des')
        em = discord.Embed(
            description=embed_des,
            color=Colour.blue()
        )
        em.set_author(name=C.CONTEXT_CREATED_ROOM.get('title'), icon_url=C.CONTEXT_CREATED_ROOM.get('icon_url'))
        await interaction.message.edit(
            embed=em,
            view=RoomUserPanel(room_model.invite_url)
        )

class RoomAgainButton(discord.ui.Button):
    def __init__(self, emoji: Emoji):
        super().__init__(
            label=Config.ROOM_CONFIRM.get('again_button').get('label'),
            custom_id=Config.ROOM_CONFIRM.get('again_button').get('id'),
            style=ButtonStyle.blurple,
            emoji=emoji,
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.is_done = True
        room_model: RoomModel = self.view.room_model
        client = self.view.client
        new_room_model = RoomModel(
            creator = room_model.creator,
            start_msg_id = room_model.start_msg_id,
            room_create_channel_id = room_model.room_create_channel_id,
            room_again_created = True
        )

        em = discord.Embed(
            description = C.CONTEXT_LANG['des'] % (await LangModel.count()),
            color = Colour.green()
        )
        em.set_author(name=C.CONTEXT_LANG['title'])
        em.description += '\n\n' + set_level(1)

        view = CreateRoomChooseLang(new_room_model, client)

        await interaction.response.edit_message(
            embed = em,
            view = view
        )

class RoomCancelButton(discord.ui.Button):
    def __init__(self, emoji: Emoji):
        super().__init__(
            label=Config.ROOM_CONFIRM.get('cancel_button').get('label'),
            custom_id=Config.ROOM_CONFIRM.get('cancel_button').get('id'),
            style=ButtonStyle.red,
            emoji=emoji,
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.is_done = True
        em = discord.Embed(
            description=C.CONTEXT_CANCEL_ROOM.get('des'),
            color = Colour.red()
        )
        em.set_author(name=C.CONTEXT_CANCEL_ROOM.get('title'))

        await interaction.response.edit_message(
            embed=em, 
            view=RoomCloseCancelView(self.view.client, self.view.room_model)
        )

class RoomCloseCancelView(discord.ui.View):
    def __init__(self, client, room_model):
        self.room_model: RoomModel = room_model
        self.client: Client = client
        self.is_done = False

        super().__init__(timeout=Config.ROOM_CREATION_TIMEOUT)

        button_yes = discord.ui.Button(
                label= 'ㅤㅤㅤYESㅤㅤㅤ',
                style=ButtonStyle.green,
                custom_id='close_yes_button',
        )
        button_yes.callback = self.callback_yes

        button_no = discord.ui.Button(
                label= 'ㅤNOㅤ',
                style=ButtonStyle.red,
                custom_id='close_no_button',

        )
        button_no.callback = self.callback_no
        

        self.add_item(button_yes)
        self.add_item(button_no)

    async def callback_yes(self, interaction: discord.Interaction):
        self.is_done = True
        em = discord.Embed(
            description=C.CONTEXT_CLOSE_ROOM.get('des'),
            color = Colour.red()
        )

        await interaction.response.edit_message(embed=em, view=None)
        channel = await self.client.fetch_channel(self.room_model.room_create_channel_id)
        
        await asyncio.sleep(10)

        await channel.delete()
        del self.room_model

    async def callback_no(self, interaction: discord.Interaction):
        self.is_done = True
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
    
    async def on_timeout(self):
        if not self.is_done:
            room_channel = await self.client.fetch_channel(self.room_model.room_create_channel_id)
            await room_channel.delete(reason='Room creation timeout')