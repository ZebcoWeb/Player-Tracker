from datetime import datetime

from mongoengine import fields, Document, CASCADE, NULLIFY

from .member import MemberModel
from .game import GameModel


__all__ = 'RoomModel'

class RoomModel(Document):
    
    member = fields.ReferenceField('MemberModel', reverse_delete_rule=CASCADE, required=True)
    start_msg_id = fields.LongField(required=True) # Msg id when create room
    room_channel_id = fields.LongField(required=True)
    status = fields.StringField(default='process')
    lang = fields.StringField(default=None)
    game = fields.ReferenceField('GameModel', reverse_delete_rule=NULLIFY, default=None)
    capacity = fields.StringField(default=None)
    mode = fields.StringField(default=None)
    bitrate = fields.StringField(default=None)
    invite_code = fields.URLField(default=None)
    tracker_msg_id = fields.LongField()
    tracker_channel_id = fields.LongField()
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






