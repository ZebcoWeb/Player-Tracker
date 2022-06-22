import os, sys, inspect, discord

from typing import List, Coroutine, Union
from string import Template
from datetime import datetime
from io import BytesIO
from PIL import Image
from beanie import Document
from pymongo import MongoClient

from discord.colour import Colour
from discord.ext.commands import Bot
from discord.app_commands import CommandTree, ContextMenu

from data.config import Config, Emoji, Channel
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
        'z': 'ᴢ',
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
    for name, obj in inspect.getmembers(sys.modules['modules.models']):
        if inspect.isclass(obj):
            if issubclass(obj, Document):

                if name in Config.IGNORE_MODELS:
                    pass
                else:
                    models.append(obj)
    return models

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

async def checks(interaction: discord.Interaction, functions: Union[List[Coroutine], Coroutine]):
    if isinstance(functions, list):
        for func in functions:
            if not await func(interaction):
                return False
        return True
    elif isinstance(functions, Coroutine):
        return await functions(interaction)

def capacity_humanize(capacity: int) -> str:
    if capacity == 2:
        return 'Due'
    elif capacity == 3:
        return 'Trio'
    elif capacity == 4:
        return 'Quad'
    elif capacity == 6:
        return 'Six'
    elif capacity == 8:
        return 'Eight'
    elif capacity == 20:
        return 'Twenty'
    elif capacity == 50:
        return 'Fifty'
    elif capacity == None:
        return 'Infinite'
    else:
        return 'Unknown'
    
async def generate_tracker_footer(client, color):
    url_generator = await client.fetch_channel(Channel.URL_GENERATOR_CHANNEL)
    footer_img = Image.new("RGB", (600, 24), color=str(color))
    buffer = BytesIO()
    footer_img.save(buffer, format="PNG")
    buffer.seek(0)
    footer_img_file = discord.File(buffer, filename="footer.png")
    message = await url_generator.send(file=footer_img_file)
    att = message.attachments[0]
    return att.url

def tracker_message_players(current_player_count: int, total_player_count: Union[int, None], closed: bool = False):
    if total_player_count == None:
        total_player_count = 'Ꝏ'
    status_str = f'{Emoji.YELLOW_DOT} *The room is currently closed*' if closed else f'{Emoji.GREEN_DOT} *The room is currently online*'
    return f"ㅤㅤㅤㅤ{Emoji.P}{Emoji.L}{Emoji.A}{Emoji.Y}\nㅤㅤㅤㅤㅤㅤㅤ{Emoji.N} {Emoji.O} {Emoji.W}\n\n {status_str} **[{current_player_count}/{total_player_count}]**\n\n**➜ Room Information**"