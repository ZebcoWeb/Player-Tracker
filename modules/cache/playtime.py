import rom

from datetime import datetime

from modules.utils import LogType, get_logger, time_diff_min


# That is, the total playing time based on each game

class PlayTime(rom.Model):

    room_id = rom.Integer(required=True, unique=True, index=True)
    start_time = rom.DateTime()


    def save(self, *args, **kwargs):
        if not self.start_time:
            self.start_time = datetime.now()
        return super(PlayTime, self).save(*args, **kwargs)



#---------
# Handlers
#---------

def playtime_handler_create(sender, document):

    try:
        
        if document.id and document.game:
            PlayTime(room_id=document.id).save()
            
    except Exception as e:

        get_logger(LogType.Cache).error('playtime_handler_create func not working: \n' + e)

        
def playtime_handler_register(sender, document):

    try:

        if document.id:
            playtime_cache = PlayTime.get_by(room_id=document.id)
            start_time = playtime_cache.start_time
            playtime_cache.delete()
            time_diffrent = time_diff_min(start_time=start_time) # Based on int minutes

            if time_diffrent >= 1:
                Game = document.game
                Game.update_one(inc__total_play_time=round(time_diffrent))

    except Exception as e:

        get_logger(LogType.Cache).error('playtime_handler_register func not working: \n' + e)


    