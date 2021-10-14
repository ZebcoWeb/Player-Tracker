import datetime

from mongoengine import fields, Document, NULLIFY

from .game import GameModel


class WikiModel(Document):
    name = fields.StringField(required=True, unique=True)
    game = fields.ReferenceField('GameModel', reverse_delete_rule=NULLIFY, default=None)
    logo_path = fields.StringField(required=True)
    banner_path = fields.StringField(default=None)
    url = fields.URLField(required=True)
    visit_value = fields.IntField(default=0)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DateTimeField()

    meta = {
        'ordering': ['-visit_value'],
        'collection': 'Wiki',
    }

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.now()
        return super(WikiModel, self).save(*args, **kwargs)
