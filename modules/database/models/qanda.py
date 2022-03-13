from datetime import datetime
from typing import Optional

from beanie import Document, Link
from pydantic import Field
from .member import MemberModel

class QandaModel(Document):
    title: str
    question: str
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