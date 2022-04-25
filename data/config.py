
from discord import ButtonStyle

class Emoji:
    CHECK_CIRCLE_TONE = '<:twotone_check_circle_white_24dp:902221842188734475'
    CANCEL_CIRCLE_TONE = '<:twotone_cancel_white_24dp:902221842201346058>'
    CREATE_CIRCLE = '<:create:962744330865496065>'
    CLICK_MOUSE = '<:twotone_ads_click_white_24dp:921362708018896916>'
    ARROW_FORWARD = '<:arrow_forwardd:870680930048671814>'
    ARROW_BACK = '<:arrow_backk:870680929868320809>'
    CURSOR = '<:cursor:962641472061063168>'
    USERS = '<:users:962779152895848498>'
    MENU = '<:menu:964589442402758758>'
    NAVBAR = '<:nanbar:965296887961903144>'
    RED_BIN = '<:redbin:964593424340758578>'

    UR = '<:ur:959358598037778492>'
    DR = '<:dr:959358557160091648>'
    HC = '<:hc:959355814517293056>'
    VC = '<:vc:959355814798307348>'
    CR = '<:cr:959355813917519893>'

    # Qoutes Emojis
    Q1 = '<:q_:959535651869585458>'
    Q2 = '<:q2:959539988574392340>'
    RS = '<:rs:959535650980368464>'
    LS = '<:ls:959535651877965864>'
    L = '<:l_:959535651051675729>'

    RANK1 = '<:rank1:959360760134397992>'
    RANK2 = '<:rank2:959360760671256586>'
    RANK3 = '<:rank3:959383794580852746>'
    RANK_OTHER = '<:rank_other:959360760599965737>'

    ENGLISH_FLAG = '<:usaflag:868206926171881583>'
    PERSIAN_FLAG = '<:iranflag:868206924032778350>'

    EMPTY_LEVEL = '<:level:949729099478356118>'
    WHITE_LEVEL = '<:level_white:949729098865979402>'
    GREEN_LEVEL = '<:level_green:949729099969085500>'

    CIRCLE = '<:circle_w:951908235051413514>'

    CHECK = '<:check:868207164001497158>'
    CLOSE = '<:cancell:868207163582083083>'

    CONFIRM_TONE_ID = 868207164001497158
    AGAIN_TONE_ID = 868207163569471570
    CANCEL_TONE_ID = 868207163582083083

    QA_ID = 952239387503104060
    
class Config:
    VERSION = '1.0.0b'
    DEBUG = False
    DISCORD_DEBUG = True
    I18N_LOCALEDIR = 'i18n'
    I18N_DOMAIN = 'base'
    SERVER_ID = 854646392197611530
    DAILY_ROOM_LIMIT_POWER = 4
    DAILY_ROOM_LIMIT_POWER_PLUS = 8
    BRAND_COLOR = 0xA600FF

    ROOM_CREATION_TIMEOUT = 300

    LEVEL_INDEX_NUM = 6

    IGNORE_MODELS = ['wiki']
    IGNORE_EXTENTIONS = ['cogs.logs', 'cogs.moderation']

    ROOM_LANGS = (
        ('en', 'English', Emoji.ENGLISH_FLAG),
        ('fa', 'Persian', Emoji.PERSIAN_FLAG),
    )
    
    ROOM_CAPACITIES = {
        'two_capacity_button' : {'emoji':925129637221249024,'capacity':2},
        'three_capacity_button' : {'emoji':925129637082841150,'capacity':3},
        'four_capacity_button' : {'emoji':925129637556801577,'capacity':4},
        'six_capacity_button' : {'emoji':925129637653274645,'capacity':6},
        'eight_capacity_button' : {'emoji':925129637921710150,'capacity':8},
        'twenty_capacity_button' : {'emoji':925129638466973718,'capacity':20},
        'fifty_capacity_button' : {'emoji':925129638936731658,'capacity':50},
        'Infinity_capacity_button' : {'emoji':925130234876010568,'capacity':None},
    }

    ROOM_BITRATES = {
        '8k_bitrate_button' : {'emoji':925140947107454987,'bitrate':8000},
        '40k_bitrate_button' : {'emoji':925140947405262848,'bitrate':40000},
        '64k_bitrate_button' : {'emoji':925140947610775562,'bitrate':64000},
        '96k_bitrate_button' : {'emoji':925140949028466760,'bitrate':96000},
    }

    ROOM_MODES = {
        'public_room_button' : {'emoji':868207163993100339 ,'mode':'public', 'label':'ㅤPublicㅤ', 'style': ButtonStyle.green},
        'private_room_button' : {'emoji':868207164420927497 ,'mode':'private', 'label':'ㅤPrivateㅤ', 'style': ButtonStyle.red},
    }

    ROOM_CONFIRM = {
        'confirm_button' : {'emoji':868207164001497158, 'id':'confirm_button', 'label':'Confirm'},
        'again_button' : {'emoji':868207163569471570, 'id':'again_button', 'label':'Again'},
        'cancel_button' : {'emoji':868207163582083083, 'id':'cancel_button', 'label':'Cancel'},
    }

    COLORS= [
        0xFF0000,0xFF1493,0xFF8C00,0xFFFF00,0xDA70D6,0x7B68EE,
        0x00FF00,0x228B22,0x00FFFF,0xFFDEAD,0xFFFFFF,0x0000FF
    ]

    COLOR_DISCORD = 0x2F3136  #gray

class Todoist:
    SECTION_ID = 70057385
    PROJECT_ID = 2278428039

    LABEL_LOW = 2158970441
    LABEL_MEDIUM = 2158970440
    LABEL_HIGH = 2158970439

class Role:
    POWER = 863414941033299979
    POWER_PLUS = 863452195555115079
    RAM = 863452008345894912
    PLAYING_NOW = 864099429211439134


class Channel:
    CREATE_ROOM = 962715094813380689
    RADIO_NEWS = 894256920255414393
    TRACKER_CHANNELS = [855199840099106847, 855354597459623957]
    JOIN_LOG = 920597444503433246
    LEAVE_LOG = 963302467850883092
    QA_CHANNEL = 866812639783288872
    QUOTE = 952524810381033482
    SUPPORT_NOTICE = 961335267506135091
    CONTACT_US = 855896054221373470
    
    DATE_STATS_VC = 952233403925790750
    ROOM_STATS_VC = 952232648686841906
    
class Category:
    ROOMS = 854646392197611534
    PLATFORM = 952108690654240838
    TICKETS = 961996224540590131
    

class Regex:
    DISCORD_INVITE_LINK = '/(https?://)?(www.)?(discord.(gg|io|me|li)|discordapp.com/invite)/.+[a-z]/g'

class Assets:
    LOGO_PURPLE = 'https://media.discordapp.net/attachments/912750358890160148/912752149090435152/logo_purple.png'
    LOGO_PURPLE_MINI = 'https://media.discordapp.net/attachments/912750358890160148/912752149090435152/logo_purple.png?width=50&height=49'
    TASK_ICON = 'https://media.discordapp.net/attachments/912750358890160148/912752149270777936/task_icon.png'
    ADD_ICON = 'https://media.discordapp.net/attachments/912750358890160148/916057441274318868/plus-circle.png'
    LFP_BANNER = 'https://media.discordapp.net/attachments/912750358890160148/916059487234846830/lfp.png'
    QUOTE_BANNER = 'https://media.discordapp.net/attachments/912750358890160148/959529389526253608/quote.png'
    HELP_ICON = 'https://cdn.discordapp.com/attachments/912750358890160148/959078018716934164/help-circle.png'