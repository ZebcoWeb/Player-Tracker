from datetime import date, datetime

from mongoengine import fields, Document, PULL, NULLIFY
from discord.client import Client

from data.config import Config
from modules.utils import LogType, get_logger

from .game import GameModel
from .wiki import WikiModel


class MemberModel(Document):

    member_id = fields.LongField(required=True)
    latest_discord_id = fields.StringField(regex='(.*)#(\d{4})')
    room_create_value = fields.IntField(default=0)
    room_join_value = fields.IntField(default=0)
    wiki_usage_value = fields.IntField(default=0)
    support_usage_value = fields.IntField(default=0)
    # TODO: create voice state handler
    total_play_time = fields.IntField(default=0) # Based on minutes
    lang = fields.StringField(default='en')
    latest_game_played = fields.ReferenceField('GameModel', reverse_delete_rule=NULLIFY, default=None)
    games_played = fields.ListField(fields.ReferenceField('GameModel' , reverse_delete_rule=PULL), default=None)
    wikis_used = fields.ListField(fields.ReferenceField('WikiModel', reverse_delete_rule=PULL), default=None)
    is_staff = fields.BooleanField(default=False)
    is_owner = fields.BooleanField(default=False)
    is_robot = fields.BooleanField(default=False)
    is_power_plus = fields.BooleanField(default=False)
    is_leaved = fields.BooleanField(default=False)
    ban_time = fields.DateTimeField(default=None)
    leaved_at = fields.DateTimeField(default=None)
    first_time_join = fields.DateTimeField() # That means created at

    # Restriction fields
    daily_room_created = fields.IntField(default=0) # This field is reset every 24 hours 

    meta = {
        'ordering': ['-first_time_join','-is_ban'],
        'collection': 'Member',
        'indexes': [
            'latest_discord_id',  # text index
        ]
    }

    def save(self, *args, **kwargs):
        if not self.first_time_join:
            self.first_time_join = datetime.now()
        return super(MemberModel, self).save(*args, **kwargs)

    
    @property
    def is_ban(self):
        if self.ban_time:
            if self.ban_time > datetime.now():
                return True
        return False

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


    # SIGNAL Handler
# def room_limit_handler(sender, document):

#     try:
#         if not document.is_staff:
#             if document.is_power_plus and document.daily_room_created:
#                 if document.daily_room_created < Config.DAILY_ROOM_LIMIT_POWER_PLUS:
#                     document.daily_room_created += 1

#             elif document.is_power and document.daily_room_created:
#                 if document.daily_room_created < Config.DAILY_ROOM_LIMIT_POWER:
#                     document.daily_room_created += 1
#         else:
#             pass
        
#     except Exception as e:
#         get_logger(LogType.Cache).error('room_limit_handler func not working: \n' + e)
