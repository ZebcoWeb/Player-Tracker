import datetime

from mongoengine import fields, Document


class GameModel(Document):
    name_key = fields.StringField(required=True, unique=True)
    emoji = fields.IntField(max_value=18, required=True)
    abbreviation = fields.StringField(max_length=5, unique=True) # That means short name
    logo_path = fields.StringField(required=True)
    banner_path = fields.StringField(required=True)
    play_time = fields.IntField(default=0) # Based on minutes
    used_value = fields.IntField(default=0)
    notif_value = fields.IntField(default=0)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DateTimeField()

    meta = {
        'ordering': ['-used_value'],
        'collection': 'Game',
    }

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.now()
        return super(GameModel, self).save(*args, **kwargs)
