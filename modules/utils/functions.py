import os, sys, inspect, discord

from typing import List
from string import Template
from datetime import datetime

from discord.colour import Colour
from discord.ext.commands import Bot
from discord.app_commands import CommandTree, ContextMenu
from beanie import Document
from pymongo import MongoClient

from data.config import Config, Emoji
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

def get_loaded_ctxs(client: Bot):
    ctxs = []
    for ctx in client.tree.walk_commands(guild=discord.Object(id=Config.SERVER_ID)):
        if isinstance(ctx, discord.app_commands.ContextMenu):
            ctxs.append(ctx.callback.__qualname__)
    return ctxs


def set_level(pointer_index=1, last=False):
    if last:
        return 'ㅤ' + (Emoji.EMPTY_LEVEL + '⠀') * (Config.LEVEL_INDEX_NUM - 1) + Emoji.GREEN_LEVEL

    level = 'ㅤ'
    for i in range(Config.LEVEL_INDEX_NUM):
        if i + 1 == pointer_index:
            level += Emoji.WHITE_LEVEL + '⠀'
        else:
            level += Emoji.EMPTY_LEVEL + '⠀'
    return level

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

def small_letter(text: str) -> str:
    string = text.lower()
    dict = {
        'a': 'ᴀ',
        'b': 'ʙ',
        'c': 'ᴄ',
        'd': 'ᴅ',
        'e': 'ᴇ',
        'f': 'ꜰ',
        'g': 'ɢ',
        'h': 'ʜ',
        'i': 'ɪ',
        'j': 'ᴊ',
        'k': 'ᴋ',
        'l': 'ʟ',
        'm': 'ᴍ',
        'n': 'ɴ',
        'o': 'ᴏ',
        'p': 'ᴘ',
        'q': 'ǫ',
        'r': 'ʀ',
        's': 'ꜱ',
        't': 'ᴛ',
        'u': 'ᴜ',
        'v': 'ᴠ',
        'w': 'ᴡ',
        'x': 'x',
        'y': 'ʏ',
        'x': 'ᴢ',
    }

    for char in string:
        if char in dict:
            string = string.replace(char, dict[char])
    return string


async def load_extentions(client):
        for path, subdirs, files in os.walk('cogs/'):
            for name in files:
                if name.endswith('.py'):
                    filename = os.path.join(path, name).replace('/', '.').replace('\\', '.')[:-3]
                    if filename not in Config.IGNORE_EXTENTIONS:
                        try:
                            await client.load_extension(filename)
                        except Exception as e:
                            print(f'! Failed to load extension {filename}.')
                            raise e

def load_ctxs(tree: CommandTree, ctx_list: List[ContextMenu]):
    for ctx in ctx_list:
            try:
                tree.add_command(ctx)
            except Exception as e:
                print(f'! Failed to load ctx {ctx.callback.__qualname__}.')
                print(e)

def inspect_models():
    models = []
    for name, obj in inspect.getmembers(sys.modules['modules.database.models']):
        if inspect.isclass(obj):
            if issubclass(obj, Document):

                if name in Config.IGNORE_MODELS:
                    pass
                else:
                    models.append(obj)
    return models

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
    

class DeltaTemplate(Template):
    delimiter = "%"

def strfdelta(tdelta, fmt):
    """Same as strftime but with a timedelta"""
    d = {"D": tdelta.days}
    d["H"], rem = divmod(tdelta.seconds, 3600)
    d["M"], d["S"] = divmod(rem, 60)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)

def smart_truncate(content, length=100, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix