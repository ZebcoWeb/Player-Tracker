import pymongo

from datetime import datetime

from beanie import Document, Indexed
from pydantic import Field

class QuoteModel(Document):
    character: str
    quote: Indexed(str, pymongo.TEXT)
    game: str
    display_count: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Collection:
        name = "quotes"

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True
    
    class Settings:
        validate_on_save = True