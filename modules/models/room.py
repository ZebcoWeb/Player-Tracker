import discord

from datetime import datetime
from typing import List, Optional, Union

from beanie import Document, Insert, Link, Indexed
from beanie.odm.actions import after_event
from pydantic import Field
from pydantic.typing import NoneType

from modules.utils import tracker_message_players

from .game import GameModel
from .member import MemberModel
from .languages import LangModel

__all__ = 'RoomModel'

class RoomModel(Document):

    creator: Link[MemberModel]              # reverse_delete_rule=CASCADE
    start_msg_id: Optional[int]             # Msg id when create room
    room_create_channel_id: Optional[int]
    room_voice_channel_id: Optional[Indexed(int, unique=True)]

    lang: Optional[Link[LangModel]]
    game: Optional[Link[GameModel]]         # reverse_delete_rule=NULLIFY
    capacity: Union[str, NoneType] = None
    mode: Optional[str]
    bitrate: Optional[str]

    likes: List[int] = []
    
    invite_url: Optional[str]
    tracker_msg_id: Optional[int]
    tracker_channel_id: Optional[int]
    is_waiting_room: bool = False
    room_again_created: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Collection:
        name = "rooms"

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True

    class Settings:
        validate_on_save = True


    async def full_delete_room(self, client: discord.Client):
        channel = await client.fetch_channel(self.room_create_channel_id)
        vc_channnel = await client.fetch_channel(self.room_voice_channel_id)
        if channel:
            await channel.delete()
        if vc_channnel:
            await vc_channnel.delete()
        if self.tracker_channel_id:
            tracker_channel = await client.fetch_channel(self.tracker_channel_id)
            tracker_msg = await tracker_channel.fetch_message(self.tracker_msg_id)
            if tracker_msg:
                embed = tracker_msg.embeds[0]
                embed.description = tracker_message_players(0, self.capacity, True)
                await tracker_msg.edit(embed=embed)
        await self.delete()

    # -------------------
    # Signals
    # -------------------

    # @after_event(Insert)
    # def daily_room_action(self):

    #     user: MemberModel = self.creator

    #     if not user.is_staff:
    #         if user.is_power_plus:
    #             if user.daily_room_created < Config.DAILY_ROOM_LIMIT_POWER_PLUS:
    #                 user.daily_room_created += 1
    #                 user.save()

    #         elif user.is_power:
    #             if user.daily_room_created < Config.DAILY_ROOM_LIMIT_POWER:
    #                 user.daily_room_created += 1
    #                 user.save()

    @after_event(Insert)
    async def update_game_used_value(self):
        if self.game:
            self.game.used_value += 1
            self.creator.latest_game_played = self.game
            await self.game.save()
        self.creator.room_create_value += 1
        await self.creator.save()