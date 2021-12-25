import os
import sys
import discord

from datetime import datetime

from discord.colour import Colour
from pymongo import MongoClient

from data.config import Todoist as TD
from modules.utils.i18n import i18n
from modules.config import Env


def time_diff_min(start_time: datetime, end_time: datetime = datetime.now()):
    """Returns the distance between two Datetimes in minutes
    """
    
    if start_time <= end_time:
        return round((end_time - start_time).total_seconds() / 60.0)
    return 0

def success_embed(msg: str, color = None):
    return discord.Embed(
        description = ':white_check_mark: ' + msg,
        color = color if color else Colour.green()
    )


def error_embed(msg: str, color = None):
    return discord.Embed(
        description = ':exclamation: ' + msg,
        color = color if color else Colour.red()
    )


def db_is_alive():
    try:

        client = MongoClient(Env.DATABASE_HOST)
        if client.server_info()['ok'] == 1:
            print('> Database is alive!')
        client.close()

    except Exception as e:
        print('> Could not connect to database!')
        print('> Exiting...')
        sys.exit(1)



class Attach:
    """Construct a Attach for local files"""
    def __init__(
        self, filepath: str) -> None:
        self.filepath = filepath.replace('\\' , '/')
    
    def __str__(self) -> str:
        return f"<Attach filepath='{self.filepath}'>"

    def __repr__(self) -> str:
        return f"<Attach filepath='{self.filepath}' filename='{self.filename}' size='{self.size} KB'>"

    @property
    def filename(self):
        return self.filepath.split('/')[-1]

    @property
    def fileobj(self):
        return discord.File(self.filepath, filename=self.filename)
    
    @property
    def url(self):
        return 'attachment://' + self.filename
    
    @property
    def size(self):
        """Return file sixe to KB"""
        return round(
            number = os.path.getsize(self.filepath) / 1024, 
            ndigits=2
        )