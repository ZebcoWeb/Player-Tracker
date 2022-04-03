from datetime import datetime
from typing import List, Optional

from beanie import Document, Indexed, Link
from discord import Client
from pydantic import Field, conint, constr
from pymongo import TEXT

from data.config import Config
from modules.utils import strfdelta

from .game import GameModel
from .wiki import WikiModel

# from modules.utils import LogType, get_logger



class MemberModel(Document):

    member_id: Indexed(conint(strict=True), unique=True)
    latest_discord_id: Indexed(str, unique=True, index_type=TEXT)

    room_create_value: conint(ge=0) = 0
    room_join_value: conint(ge=0) = 0
    wiki_usage_value: conint(ge=0) = 0
    support_usage_value: conint(ge=0) = 0
    question_answered_count: conint(ge=0) = 0
    # TODO: create voice state handler
    total_play_time: conint(ge=0) = 0   # Based on minutes
    lang: constr(max_length=3) = 'en'

    latest_game_played: Optional[Link[GameModel]]
    games_played: List[Link[GameModel]] = []
    wikis_used: List[Link[WikiModel]] = []

    is_staff: bool = False
    is_owner: bool = False
    is_robot: bool = False
    is_power: bool = True
    is_power_plus: bool = False
    is_ban_forever: bool = False
    is_leaved: bool = False

    ban_time: Optional[datetime]
    leaved_at: Optional[datetime]
    crated_at: datetime = Field(default_factory=datetime.utcnow)  # That means created at

    # daily_room_created: conint(ge=0) = 0                          # This field is reset every 24 hours 

    class Collection:
        name = "members"

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True
    
    @property
    def is_ban(self):
        if self.ban_time:
            if self.ban_time > datetime.now():
                return True
        return False
    
    @property
    def ban_time_str(self):
        if self.is_ban:
            timedelta = self.ban_time - datetime.now()
            return strfdelta(timedelta, '%D days %H:%M:%S')
        return None

    @property
    def is_create_room(self):
        return True if self.room_create_value != 0 else False

    @property
    def is_join_room(self):
        return True if self.room_join_value != 0 else False

    @property
    def is_use_wiki(self):
        return True if self.wiki_usage_value != 0 else False
    

    async def fetch_member(self, client: Client):
        guild = await client.fetch_guild(Config.SERVER_ID)

        return await guild.fetch_member(self.member_id)
