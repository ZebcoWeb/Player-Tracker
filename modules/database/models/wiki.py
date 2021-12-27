from datetime import datetime, timedelta
from typing import Optional

import aiohttp
from aiowiki import Wiki
from beanie import Document, Indexed, Link
from pydantic import Field, conint, constr
from pymongo import TEXT

# from modules.utils import Attach
from .game import GameModel


class WikiModel(Document):
    
    name: Indexed(constr(strict=True, max_length=40, regex='^[A-Za-z0-9_]+$'), unique=True, index_type=TEXT)
    game: Optional[Link[GameModel]]     # reverse_delete_rule=NULLIFY
    logo_path: constr(strict=True)      # need to regex
    banner_path: Optional[str]
    parent_site: constr(max_length=30) = 'fandom.com'
    subdomain: constr(strict=True, max_length=35, regex='^[A-Za-z0-9_]+$', to_lower=True)
    visit_value: conint(ge=0) = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Collection:
        name = "wikis"
    class Settings:
        use_cache = True
        cache_expiration_time = timedelta(minutes=30)

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True

    # @property
    # def attach_logo_path(self):
    #     return Attach(self.logo_path)

    # @property
    # def attach_banner_path(self):
    #     return Attach(self.banner_path) if self.banner_path else None
    
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
    async def is_online(self):
        status_code = await self.status_code

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
    
    
