from mongoengine import signals

from modules.database.models import RoomModel
from modules.cache.playtime import playtime_handler_create, playtime_handler_register



signals.post_save.connect(playtime_handler_create, sender=RoomModel) # Cache
signals.post_delete.connect(playtime_handler_register, sender=RoomModel) # Cache