from mongoengine import signals

from modules.database.models import RoomModel, MemberModel
from modules.cache.playtime import playtime_handler_create, playtime_handler_register
from modules.database.models.member import room_limit_handler



signals.post_save.connect(playtime_handler_create, sender=RoomModel) # Cache
signals.post_delete.connect(playtime_handler_register, sender=RoomModel) # Cache
signals.pre_save_post_validation.connect(room_limit_handler, sender=MemberModel) # limit member room