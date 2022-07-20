import functools
import aiohttp
import re

from discord import Interaction, app_commands

from modules.models import MemberModel, RoomModel
from data.config import Channel, Emoji, Config
from modules.utils import error_embed


async def is_ban_handler(interaction: Interaction):
    member_model = await MemberModel.find_one({'member_id': interaction.user.id})
    if member_model:
        if member_model.is_ban_forever:
            await interaction.response.send_message(
                embed=error_embed('You are banned from the platform forever.'),
                ephemeral=True
            )
            return False
        elif member_model.is_ban:
            await interaction.response.send_message(
                embed= error_embed(f'You are banned on the platform for another `{member_model.ban_time_str}`, please wait until then.'),
                ephemeral=True
            )
            return False
        else:
            return True
    else:
        return True 
        #TODO: Add a message to the user that they are not registered

def is_ban():
    async def predicate(interaction: Interaction):
        return await is_ban_handler(interaction)
    return app_commands.check(predicate)
    
async def had_room_handler(interaction: Interaction):
    if interaction.user:
        user_room = await RoomModel.find(RoomModel.creator.member_id == interaction.user.id, fetch_links=True).to_list()
        if user_room == []:
            return True
        else:
            await interaction.response.send_message(
                embed=error_embed(f'You already have a room. Delete the previous room to create a new one.\n\n▸ If your room is not available on the server, send a ticket to <#{Channel.CONTACT_US}>'),
                ephemeral=True
            )
            return False

def had_room():
    async def predicate(interaction: Interaction):
        return await had_room_handler(interaction)
    return app_commands.check(predicate)


async def is_inviter_handler(interaction: Interaction):
    if 'custom_id' in list(interaction.data.keys()):
        custom_id = interaction.data['custom_id']
    else:
        custom_id = None
    if custom_id not in Config.IGNORE_INVITE_CHECKER:
        member = await MemberModel.find_one(MemberModel.member_id == interaction.user.id)
        if member:
            if not member.is_staff or member.is_owner:
                if member.invite_count == 0:
                    await interaction.response.send_message(
                        embed=error_embed('You must invite at least **one** of your friends to use the features of the platform.'),
                        ephemeral=True
                    )
                    return False
    return True

def is_inviter():
    async def predicate(interaction: Interaction):
        return await is_inviter_handler(interaction)
    return app_commands.check(predicate)


async def is_media(url: str):
    if re.match("^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$", url):
        async with aiohttp.ClientSession() as session:
            async with session.head(url) as res:
                content_type = res.headers.get('content-type')
                if content_type.startswith('image/'):
                    return url
                else:
                    return None
    else:
        return None