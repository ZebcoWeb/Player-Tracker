import humanize
import datetime

from discord.ext import commands, tasks

from data.config import Channel
from modules.database.models import RoomModel


class Tasks(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client
        self.room_stats_channel = self.client.get_channel(Channel.ROOM_STATS_VC)
        self.date_stats_channel = self.client.get_channel(Channel.DATE_STATS_VC)

        self.update_date_stats.start()
        self.update_room_stats.start()


    # Task to update date stats
    @tasks.loop(seconds=10)
    async def update_date_stats(self):
        try:
            now = datetime.datetime.now()
            day = now.day
            date_str = datetime.datetime.strftime(now, '—  %b {}, %Y ').format(humanize.ordinal(day)) + '🪐'

            await self.date_stats_channel.edit(
                name = date_str
            )
        except:
            pass

    # Task to update room stats
    @tasks.loop(seconds=30)
    async def update_room_stats(self):
        try:
            count = await RoomModel.find().count()
            await self.room_stats_channel.edit(
                name = f'—  {count} Room Now 👾'
            )
        except:
            pass


async def setup(client:commands.Bot):
    await client.add_cog(Tasks(client))