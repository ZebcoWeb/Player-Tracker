import datetime

from mongoengine import fields, Document




class MemberModel(Document):

    member_id = fields.IntField(max_value=18, required=True)
    room_create_value = fields.IntField(default=0)
    room_join_value = fields.IntField(default=0)
    wiki_usage_value = fields.IntField(default=0)
    support_usage_value = fields.IntField(default=0)
    lang = fields.StringField(default=None)
    games_played = fields.ListField(fields.ReferenceField('GameModel'), default=None)
    wikis_used = fields.ListField(fields.ReferenceField('WikiModel'), default=None)
    is_staff = fields.BooleanField(default=False)
    is_ban = fields.BooleanField(default=False)
    is_power_plus = fields.BooleanField(default=False)
    is_leave = fields.BooleanField(default=False)
    leaved_at = fields.DateTimeField(default=None)
    first_time_join = fields.DateTimeField() # That means created at

    meta = {
        'ordering': ['-first_time_join','-is_ban'],
        'collection': 'Member',
    }

    def save(self, *args, **kwargs):
        if not self.first_time_join:
            self.first_time_join = datetime.now()
        return super(MemberModel, self).save(*args, **kwargs)
    
