from datetime import datetime, timedelta
from typing import Optional

from beanie import Document, Indexed
from discord import Client, Emoji
from pydantic import Field, conint, constr
from pymongo import TEXT

# from modules.utils import Attach

class GameModel(Document):
    
    name_key: Indexed(constr(strict=True, max_length=40, regex='^[A-Za-z0-9_]+$'), unique=True, index_type = TEXT)
    emoji: conint(strict=True)
    short: constr(strict=True, max_length=5, regex='^[A-Za-z0-9_]+$')
    logo_path: constr(strict=True)        # need to regex
    banner_path: Optional[str]            # need to regex
    total_play_time: conint(ge=0) = 0     # Based on minutes
    used_value: conint(ge=0) = 0
    notif_value: conint(ge=0) = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Collection:
        name = "games"

    class Settings:
        use_cache = True
        cache_expiration_time = timedelta(minutes=15)

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True


    # @property
    # def attach_logo_path(self):
    #     return Attach(self.logo_path)

    # @property
    # def attach_banner_path(self):
    #     return Attach(self.banner_path) if self.banner_path else None

    @staticmethod
    async def active_games(ignore_cache: bool = False) -> list:
        return await GameModel.find({"is_active": True}, ignore_cache=ignore_cache).to_list()

    @staticmethod
    async def trend_games(ignore_cache: bool = False) -> list:
        return await GameModel.find(
            {"is_active": True}, 
            ignore_cache=ignore_cache
            ).sort(-GameModel.used_value).to_list()

    @staticmethod
    async def best_play_time(ignore_cache: bool = False) -> list:
        return await GameModel.find(
            {"is_active": True}, 
            ignore_cache=ignore_cache
            ).sort(-GameModel.total_play_time).to_list()


    def get_emoji(self, client: Client) -> Emoji:
        '''Return Emoji discord class object'''
        return client.get_emoji(self.emoji)