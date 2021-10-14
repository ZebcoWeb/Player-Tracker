import os

from discord import Intents
from discord.ext.commands import Bot





def run_discord_client():
    client = Bot(
        help_command=None,
        command_prefix='!',
        intents=Intents().all()
    )

    client.run('ODU0NjQ3Mjc5Njc1Mzc1NjM2.YMm-Tg.iIOkqDmjlUxY1B5c86IQAq8PHsg')



if __name__ == '__main__':
    run_discord_client()



