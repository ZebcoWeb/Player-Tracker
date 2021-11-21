from datetime import datetime

from mongoengine import fields, Document
from discord import Client, Emoji

from modules.utils import Attach


class GameModel(Document):
    
    name_key = fields.StringField(required=True, unique=True)
    emoji = fields.LongField(required=True)
    abbreviation = fields.StringField(required=True, max_length=5, unique=True) # That means short name
    logo_path = fields.StringField(required=True)
    banner_path = fields.StringField(default=None)
    total_play_time = fields.IntField(default=0) #! Based on minutes
    used_value = fields.IntField(default=0)
    notif_value = fields.IntField(default=0)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DateTimeField()

    meta = {
        'ordering': ['-used_value'],
        'collection': 'Game',
        'indexes': [
            'name_key',  # text index
        ]
    }


    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.now()
        return super(GameModel, self).save(*args, **kwargs)
    

    def fetch_emoji(self, client: Client) -> Emoji:
        '''Return Emoji discord class object'''
        return client.get_emoji(self.emoji)
    
    @property
    def attach_logo_path(self):
        return Attach(self.logo_path)

    @property
    def attach_banner_path(self):
        return Attach(self.banner_path) if self.banner_path else None