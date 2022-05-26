import discord

from datetime import datetime, timedelta
from typing import List, Optional
from beanie import Document, Indexed, Link, Replace, after_event
from pydantic import Field, conint, BaseModel
from pymongo import TEXT

from modules.utils import strfdelta
from data.config import Role

from .game import GameModel
from .wiki import WikiModel
from .languages import LangModel

class MemberShort(BaseModel):
    member_id: int

class MemberModel(Document):

    member_id: Indexed(conint(strict=True), unique=True)
    latest_discord_id: Indexed(str, unique=True, index_type=TEXT)

    room_create_value: conint(ge=0) = 0
    room_join_value: conint(ge=0) = 0
    wiki_usage_value: conint(ge=0) = 0
    support_usage_value: conint(ge=0) = 0
    question_asked_count: conint(ge=0) = 0
    question_answered_count: conint(ge=0) = 0
    invite_count: conint(ge=0) = 0
    lang: Optional[Link[LangModel]]
    total_play_time: Optional[timedelta]

    latest_game_played: Optional[Link[GameModel]]
    games_played: List[Link[GameModel]] = []
    wikis_used: List[Link[WikiModel]] = []
    survey_result = Optional[Link[None]]

    is_staff: bool = False
    is_surveyed: bool = False
    is_owner: bool = False
    is_power: bool = True
    is_power_plus: bool = False
    is_ban_forever: bool = False
    is_leaved: bool = False

    leaved_at: Optional[datetime]
    ban_time: Optional[datetime]
    crated_at: datetime = Field(default_factory=datetime.utcnow)  # That means created at

    daily_room_created: conint(ge=0) = 0       # This field is reset every 24 hours 

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

    @staticmethod
    async def survey_users():
        list = []
        query = await MemberModel.find_many(
            MemberModel.is_surveyed == False,
            MemberModel.is_leaved == False,
            fetch_links=True
        ).to_list()
        if query:
            list = [user for user in query if (user.room_create_value + user.question_asked_count) >= 5]
        return list


    @staticmethod
    async def join_member(member: discord.Member):
        if not member.bot:
            member_model = await MemberModel.find_one(MemberModel.member_id == member.id)
            if not member_model:
                member_model = MemberModel(
                    member_id = member.id,
                    latest_discord_id = member.name + "#" + member.discriminator,
                    is_robot= True if member.bot else False
                )
                await member_model.save()
            else:
                member_model.latest_discord_id = member.name + "#" + member.discriminator
                member_model.is_leaved = False
                member_model.leaved_at = None
                await member_model.save()

            if member_model.is_power_plus:
                await member.add_roles(discord.Object(id=Role.POWER_PLUS))
            elif member_model.is_power:
                await member.add_roles(discord.Object(id=Role.POWER))
    
    @staticmethod
    async def leave_member(member: discord.Member):
        if not member.bot:
            member_model = await MemberModel.find_one(MemberModel.member_id == member.id)
            if member_model:
                member_model.is_leaved = True
                member_model.leaved_at = datetime.now()
                await member_model.save()
    
    @staticmethod
    async def members_id_list():
        query = await MemberModel.find({}).project(MemberShort).to_list()
        return [member.member_id for member in query]