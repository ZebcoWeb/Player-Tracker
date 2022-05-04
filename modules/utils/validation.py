import functools
import aiohttp
import re

from discord import Interaction, app_commands

from modules.database.models import MemberModel, RoomModel
from data.config import Channel, Emoji
from modules.utils import error_embed


def is_ban_view(func):
    @functools.wraps(func)
    async def predicate(view , button, interaction, *args, **kwargs):
        member_model = await MemberModel.find_one(MemberModel.member_id == interaction.user.id)
        if member_model:
            if member_model.is_ban_forever:
                await interaction.response.send_message(
                    embed=error_embed('You are banned from the platform forever.'),
                    ephemeral=True
                )
            elif member_model.is_ban:
                await interaction.response.send_message(
                    embed= error_embed(f'You are banned on the platform for another `{member_model.ban_time_str}`, please wait until then.'),
                    ephemeral=True
                )
            else:
                return await func(view, button, interaction, *args, **kwargs)
        else:
            pass
            # TODO: Add a new member to the database
    return predicate


def had_room(func):
    @functools.wraps(func)
    async def predicate(view, interaction, button, *args, **kwargs):
        if interaction.user:
            user_room = await RoomModel.find(RoomModel.creator.member_id == interaction.user.id, fetch_links=True).to_list()
            if user_room == []:
                return await func(view, button, interaction, *args, **kwargs)
            else:
                await interaction.response.send_message(
                    embed=error_embed(f'You already have a room. Delete the previous room to create a new one.\n\n{Emoji.CIRCLE} If your room is not available on the server, send a ticket to <#{Channel.CONTACT_US}>'),
                    ephemeral=True
                )
    return predicate


def is_ban():
    async def predicate(interaction: Interaction):
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
            pass
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