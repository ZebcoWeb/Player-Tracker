from datetime import datetime, timedelta
from beanie import Document, Indexed
from pydantic import Field, conint, constr
from pymongo import TEXT

class LangModel(Document):

    name: Indexed(constr(strict=True, max_length=40), unique=True, index_type = TEXT)
    emoji: int
    short: constr(strict=True, max_length=5, regex='^[A-Za-z0-9_]+$')
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Collection:
        name = "languages"

    class Settings:
        use_cache = True
        cache_expiration_time = timedelta(minutes=15)

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True

    @staticmethod
    async def active_langs(ignore_cache: bool = False) -> list:
        list = await LangModel.find(LangModel.is_active == True, ignore_cache=ignore_cache).to_list()
        return list
    
    @staticmethod
    async def most_used_langs(ignore_cache: bool = False) -> list:
        return await LangModel.find(
            LangModel.is_active == True, 
            ignore_cache=ignore_cache
            ).sort(-LangModel.used_value).to_list()