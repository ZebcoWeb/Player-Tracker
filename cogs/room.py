import discord
import copy

from discord.app_commands import Group, ContextMenu
from discord.ext import commands
from discord import app_commands

from data.config import Config, Channel, Assets, Emoji
from modules.database.models.member import MemberModel
from modules.view import CreateRoomView, RoomPlayerCountButton, RoomSendInvite
from modules.utils import error_embed, success_embed, tracker_message_players
from modules.database import RoomModel


class Room(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client
        self.room_context = None
        self.view = None
        self.client.ctx_menus.append(
            ContextMenu(name='📩 Send room invite', callback=self.send_room_invite_url, guild_ids=[Config.SERVER_ID])
        )

        # self.client.loop.create_task(self.send_room_context())

    async def cog_load(self):
        await self.send_room_context()


    room = Group(name='room', description='Room commands', guild_ids=[Config.SERVER_ID])
    
    async def send_room_context(self):
        channel = await self.client.fetch_channel(Channel.CREATE_ROOM)

        async for message in channel.history():
            await message.delete()
        description = f'**Looking for player to play with?** By creating your own room, you can compete with other players like a virtual gamenet and test yourself in group or multiplayer games.\n\n<:circle_w:951908235051413514> If you want to become a member of another player\'s room, you can see the latest created rooms in the tracker channels:\n> <#{Channel.TRACKER_CHANNELS[0]}>\n> <#{Channel.TRACKER_CHANNELS[1]}>\n'
        em = discord.Embed(
            description=description,
            color=Config.COLOR_DISCORD
        )
        em.set_image(url=Assets.LFP_BANNER)
        em.set_author(name='Create your own room', icon_url=Assets.PLAY)

        self.view = CreateRoomView(client=self.client)
        self.view.add_item(RoomPlayerCountButton())

        self.room_context = await channel.send(
            embed=em,
            view=self.view
        )
        return channel


    @room.command(name='context', description='send room context (admin only)')
    @app_commands.checks.has_permissions(administrator=True)
    async def room_msg(self, interaction: discord.Interaction) -> None:
        channel = await self.send_room_context()
        await interaction.response.send_message(
            embed=success_embed(f'created room context in {channel.mention}'),
            ephemeral=True,
        )
    
    @room.command(name='remove', description='remove a room (admin only)')
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(room_id='room voice channel id')
    async def remove_room(self, interaction: discord.Interaction, room_id: str) -> None:
        room_id = int(room_id)
        room_model = await RoomModel.find_one(RoomModel.room_voice_channel_id == room_id)
        if room_model:
            try:
                await room_model.full_delete_room(interaction.client)
            except:
                pass
            finally:
                await interaction.response.send_message(
                    embed=success_embed(f'Removed room: `{room_id}`'),
                    ephemeral=True,
                )
        else:
            await interaction.response.send_message(
                embed=error_embed(f'Room `{room_id}` not found'),
                ephemeral=True,
            )

    async def add_player_count_number(self, room, current_player):
        button: discord.Button = discord.utils.find(lambda b: b.custom_id == 'player_count_button', self.view.children)
        tracker_channel = await self.client.fetch_channel(room.tracker_channel_id)
        tracker_msg = await tracker_channel.fetch_message(room.tracker_msg_id)
        if button:
            new_button = copy.copy(button)
            self.view.remove_item(button)
            player_count = int(new_button.label[0]) + 1
            new_button.label = f'{player_count} Players'
            self.view.add_item(new_button)
        embed = tracker_msg.embeds[0]
        embed.description = tracker_message_players(current_player, room.capacity)
        await tracker_msg.edit(embed=embed)


    async def reduce_player_count_number(self, room, current_player):
        button: discord.Button = discord.utils.find(lambda b: b.custom_id == 'player_count_button', self.view.children)
        tracker_channel = await self.client.fetch_channel(room.tracker_channel_id)
        tracker_msg = await tracker_channel.fetch_message(room.tracker_msg_id)
        if button:
            new_button = copy.copy(button)
            if int(new_button.label[0]) > 0:
                self.view.remove_item(button)
                player_count = int(new_button.label[0]) - 1
                new_button.label = f'{player_count} Players'
                self.view.add_item(new_button)
        embed = tracker_msg.embeds[0]
        embed.description = tracker_message_players(current_player, room.capacity)
        await tracker_msg.edit(embed=embed)


    @commands.Cog.listener('on_voice_state_update')
    async def update_player_counter(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if self.room_context:
            if after.channel:
                channel = after.channel
            else:
                channel = before.channel
            room_model = await RoomModel.find_one(RoomModel.room_voice_channel_id == channel.id)
            if room_model:
                if after.channel:
                    await self.add_player_count_number(room=room_model, current_player=len(channel.members))
                    await MemberModel.find_one(MemberModel.member_id == member.id).inc({MemberModel.room_join_value: 1})
                elif before.channel:
                    await self.reduce_player_count_number(room=room_model, current_player=len(channel.members))
                await self.room_context.edit(view=self.view)


    async def send_room_invite_url(self, interaction: discord.Interaction, user: discord.Member):
        room_model = await RoomModel.find(RoomModel.creator.member_id == interaction.user.id, fetch_links=True).to_list()
        room_model = room_model[0]
        if room_model:
            if not user.bot:
                if interaction.user != user:
                    try:
                        em = discord.Embed(
                            title=f'📩 {interaction.user.name}#{interaction.user.discriminator} invited you to a new game room',
                            description= f'\nPlayer **{interaction.user.name}** has invited you to a game room. If he/she is your **friend**, it is better not to reject the request 🤨',
                            color=Config.BRAND_COLOR
                        )
                        em.set_thumbnail(url=interaction.user.display_avatar.url)
                        em.set_footer(text=f'Player Tracker', icon_url=Assets.LOGO_PURPLE_MINI)
                        await user.send(embed=em, view=RoomSendInvite(client=self.client, room_model=room_model))
                        await interaction.response.send_message(
                            embed=success_embed(f'Invite URL successfully sent to {user.mention}'),
                            ephemeral=True,
                        )
                    except discord.HTTPException:
                        await interaction.response.send_message(
                            embed=error_embed(f'{user.mention} is not accepting direct messages. please let him/her know about this problem and try again.'),
                            ephemeral=True,
                        )
                else:
                    await interaction.response.send_message(
                        embed=error_embed(f'You can\'t invite yourself to a room. wtf...'),
                        ephemeral=True,
                    )
            else:
                await interaction.response.send_message(
                    embed=error_embed('You can\'t invite bots to your room'),
                    ephemeral=True,
                )
        else:
            await interaction.response.send_message(
                embed=error_embed(f'You don\'t have any rooms right now'),
                ephemeral=True,
            )


    


async def setup(client:commands.Bot):
    await client.add_cog(Room(client))