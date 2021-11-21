import aiohttp
import asyncio

from datetime import datetime

from mongoengine import fields, Document, NULLIFY
from aiowiki import Wiki

from modules.utils import Attach
from .game import GameModel


class WikiModel(Document):
    
    name = fields.StringField(required=True, unique=True)
    game = fields.ReferenceField('GameModel', reverse_delete_rule=NULLIFY, default=None)
    logo_path = fields.StringField(required=True)
    banner_path = fields.StringField(default=None)
    parent_site = fields.StringField(default='fandom.com')
    subdomain = fields.StringField(required=True)
    visit_value = fields.IntField(default=0)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DateTimeField()

    meta = {
        'ordering': ['-visit_value'],
        'collection': 'Wiki',
        'indexes': [
            'name',  # text index
        ]
    }

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.now()
        return super(WikiModel, self).save(*args, **kwargs)
    

    @property
    def attach_logo_path(self):
        return Attach(self.logo_path)

    @property
    def attach_banner_path(self):
        return Attach(self.banner_path) if self.banner_path else None
    
    @property
    def link(self):
        return 'https://' + self.subdomain + f'.{self.parent_site}'

    @property
    def api_link(self):
        return self.link + '/api.php'


    @property
    async def status_code(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_link) as response:
                return response.status

    @property
    def is_online(self):
        status_code = asyncio.run(self.status_code)

        return True if status_code == 200 else False
        
    @property
    def wiki(self):
        if self.is_active:
            if self.is_online:
                return Wiki(base_url=self.api_link)
            else:
                pass
            # TODO: riase error for not online
        else:
            pass
        # TODO: raise error for not active
    
    
