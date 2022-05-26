from datetime import datetime
from enum import Enum
from typing import Optional

from beanie import Document, Link
from pydantic import Field

from .member import MemberModel

class UXEnum(str, Enum): # User exxperience
    bad = 'Bad'
    good = 'Good'
    excellent = 'Excellent'


class SectionEnum(str, Enum):
    room = 'Gaming Room'
    qanda = 'Q&A'
    other = 'Other'


class SupportEnum(str, Enum):
    poor = 'Poor'
    strong = 'Strong'
    

class SurveyModel(Document):
    target_user: Link[MemberModel]
    channel_id: Optional[int]
    ux_choice: Optional[UXEnum]
    section_choice: Optional[SectionEnum]
    support_choice: Optional[SupportEnum]
    suggestion: Optional[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Collection:
        name = "surveys"

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True
    
    class Settings:
        validate_on_save = True