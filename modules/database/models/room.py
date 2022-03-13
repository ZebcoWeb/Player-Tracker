from datetime import datetime
from typing import Optional, Union

from beanie import Document, Insert, Link, Indexed
from beanie.odm.actions import after_event
from discord.client import Client
from pydantic import Field, constr, conint
from pydantic.typing import NoneType

from data.config import Config, Regex

from .game import GameModel
from .member import MemberModel

__all__ = 'RoomModel'

class RoomModel(Document):

    creator: Link[MemberModel]              # reverse_delete_rule=CASCADE
    start_msg_id: Optional[int]             # Msg id when create room
    room_create_channel_id: Optional[int]
    room_voice_channel_id: Optional[Indexed(int, unique=True)]

    lang: Optional[constr(max_length=3)]
    game: Optional[Link[GameModel]]         # reverse_delete_rule=NULLIFY
    capacity: Union[str, NoneType] = None
    mode: Optional[str]
    bitrate: Optional[str]
    
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


    async def fetch_create_room_channel(self, client: Client):
        return await client.fetch_channel(self.room_create_channel_id)
    
    async def fetch_start_msg(self, client: Client):
        return await self.fetch_create_room_channel(client).fetch_message(self.start_msg_id) if self.start_msg_id else None

    async def fetch_voice_channel(self, client: Client):
        return await client.fetch_channel(self.room_voice_channel_id) if self.room_voice_channel_id else None

    async def fetch_tracker_channel(self, client: Client):
        return await client.fetch_channel(self.tracker_channel_id) if self.tracker_channel_id else None
    
    async def fetch_tracker_msg(self, client: Client):
        return await self.fetch_tracker_channel(client).fetch_message(self.tracker_msg_id) if self.tracker_msg_id else None

    async def fetch_invite(self, client: Client):
        return await client.fetch_invite(url=self.invite_url)

    # -------------------
    # Signals
    # -------------------

    @after_event(Insert)
    def daily_room_action(self):

        user: MemberModel = self.creator

        if not user.is_staff:
            if user.is_power_plus:
                if user.daily_room_created < Config.DAILY_ROOM_LIMIT_POWER_PLUS:
                    user.daily_room_created += 1
                    user.save()

            elif user.is_power:
                if user.daily_room_created < Config.DAILY_ROOM_LIMIT_POWER:
                    user.daily_room_created += 1
                    user.save()