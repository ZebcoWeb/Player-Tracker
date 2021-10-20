import logging

from discord_webhook import DiscordWebhook, DiscordEmbed

from modules.utils.enums import LogType



__all__ = ['get_logger']


def set_embed_color(value: int):
    #embed color
    if value in [10,20]:
        return '0x00BFFF' # blue
    elif value == 30:
        return '0xFFFF00' # yellow
    elif value == 40:
        return '0xFFA500' # orange
    elif value == 50:
        return '0xFF0000' # red
    else:
        return '0x00BFFF' # blue
        
# Discord Handler Class

class DiscordHandler(logging.Handler):

    def emit(self, record):

        log_entry = self.format(record)
        embed = DiscordEmbed(
            description=log_entry, 
            color=set_embed_color(record.levelno)
            )
        embed.set_footer(text='Player Tracker Log System')
        discord_webhook = DiscordWebhook(
            url='https://discord.com/api/webhooks/876140557569757184/Ayldf7G-eGz73k0lnySoTJNkNafF5UFgEcrTFFOzi1fpyGTr8L4_7qnJRHSx9w7VJPGY'
            )
        discord_webhook.add_embed(embed)
        return discord_webhook.execute()

def add_handler(name, filename):

    # Create a custom logger
    logger = logging.getLogger(name)

    logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.INFO)

    # Print log handler
    c_handler = logging.StreamHandler()
    c_format = logging.Formatter('[%(name)s] %(levelname)s -> %(message)s')
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)

    # File log handler
    log_path = 'data/' + filename + '.txt'
    f_handler = logging.FileHandler(filename=log_path, encoding='utf-8', mode='a')
    f_format = logging.Formatter('(%(asctime)s) [%(name)s] %(levelname)s -> %(message)s')
    f_handler.setFormatter(f_format)
    logger.addHandler(f_handler)

    # Discord log handler
    d_handler = DiscordHandler()
    d_format = logging.Formatter('**`[%(name)s]`** **%(levelname)s** : %(message)s\n\n**Path:**\n%(pathname)s \n\n- %(asctime)s')
    d_handler.setFormatter(d_format)
    logger.addHandler(d_handler)
    

    return logger


# Create log message func
def get_logger(name: str = LogType.Test):
    return add_handler(str(name), 'logs')