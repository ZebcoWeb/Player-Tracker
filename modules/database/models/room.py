from datetime import datetime
from discord.client import Client

from mongoengine import fields, Document, CASCADE, NULLIFY

from .member import MemberModel
from .game import GameModel


__all__ = 'RoomModel'

class RoomModel(Document):
    ROOM_STATUS = (
        'process', 'complete'
    )
    creator = fields.ReferenceField('MemberModel', reverse_delete_rule=CASCADE, required=True)
    start_msg_id = fields.LongField(required=True) # Msg id when create room
    room_create_channel_id = fields.LongField(required=True)
    room_voice_channel_id = fields.LongField(required=False)
    status = fields.StringField(default='process', choices=ROOM_STATUS)
    lang = fields.StringField(default=None)
    game = fields.ReferenceField('GameModel', reverse_delete_rule=NULLIFY, default=None)
    capacity = fields.StringField(default=None)
    mode = fields.StringField(default=None)
    bitrate = fields.StringField(default=None)
    invite_url = fields.URLField(default=None)
    tracker_msg_id = fields.LongField(default=None)
    tracker_channel_id = fields.LongField(default=None)
    is_waiting_room = fields.BooleanField(default=False)
    room_again_created = fields.BooleanField(default=False)
    created_at = fields.DateTimeField()

    meta = {
        'ordering': ['-created_at'],
        'collection': 'Room',
    }

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.now()
        return super(RoomModel, self).save(*args, **kwargs)


    async def fetch_create_room_channel(self, client: Client):
        return await client.fetch_channel(self.room_create_channel_id)
    
    async def fetch_start_msg(self, client: Client):
        return await self.fetch_create_room_channel(client).fetch_message(self.start_msg_id) if self.start_msg_id else None

    async def fetch_voice_channel(self, client: Client):
        return await client.fetch_channel(self.room_voice_channel_id) if self.room_voice_channel_id else None

    async def fetch_tracker_channel(self, client: Client):
        return await client.fetch_channel(self.tracker_channel_id) if self.tracker_channel_id else None
    
    async def fetch_tracker_msg(self, client: Client):
        return await self.fetch_tracker_channel(client).fetch_message(self.tracker_msg_id) if self.tracker_msg_id else None

    async def fetch_invite(self, client: Client):
        return await client.fetch_invite(url=self.invite_url)





