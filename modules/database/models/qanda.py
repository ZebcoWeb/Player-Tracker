import pymongo

from datetime import datetime
from typing import Optional, Union

from beanie import Document, Link, Indexed
from beanie.odm.operators.find.evaluation import Text
from pydantic import Field, BaseModel
from .member import MemberModel


class GameShortView(BaseModel):
    game: Union[str, None]

class SearchShortView(BaseModel):
    title: str
    is_answered: bool
    search_query: str

class QandaModel(Document):
    title: str
    question: str
    search_query: Indexed(str, pymongo.TEXT)
    answer: Optional[str]
    game: Optional[str]
    questioner: Link[MemberModel]
    answerer: Optional[Link[MemberModel]]
    thread_id: int
    question_message_id: int 
    answer_message_id: Optional[int]
    is_answered: bool = False
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Collection:
        name = "qanda"

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True
    
    class Settings:
        validate_on_save = True
    
    @staticmethod
    async def games(ignore_cache: bool = False) -> list:
        query = await QandaModel.find({"is_active": True}, ignore_cache=ignore_cache).project(GameShortView).to_list()
        return list(set([game.game for game in query]))


    @staticmethod
    async def search(current: str) -> list:
        results = await QandaModel.find(
            Text(search=current, case_sensitive=False, diacritic_sensitive=False),
            {'is_active': True},
        ).sort('-created_at').project(SearchShortView).limit(7).to_list()
        return results