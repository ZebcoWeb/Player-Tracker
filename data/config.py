


class Emoji:
    CHECK_CIRCLE_TONE = '<:twotone_check_circle_white_24dp:902221842188734475'
    CANCEL_CIRCLE_TONE = '<:twotone_cancel_white_24dp:902221842201346058>'
    CREATE_CIRCLE_TONE = '<:create_ticket:868207164106342460>'
    CLICK_MOUSE = '<:twotone_ads_click_white_24dp:921362708018896916>'
    BIN_TONE = '<:twotone_delete_white_24dp:905866139031179365>'
    ARROW_FORWARD = '<:arrow_forwardd:870680930048671814>'
    ARROW_BACK = '<:arrow_backk:870680929868320809>'

    ENGLISH_FLAG = '<:usaflag:868206926171881583>'
    PERSIAN_FLAG = '<:iranflag:868206924032778350>'

    EMPTY_LEVEL = '<:e1:921853788858511361>'
    WHITE_FILL_LEVEL = '<:e2:921851166021787709>'
    GREEN_FILL_LEVEL = '<:e3:921851166080528455>'

    TEST = (f'{EMPTY_LEVEL}' * 7)

    CONFIRM_TONE_ID = 868207164001497158
    AGAIN_TONE_ID = 868207163569471570
    CABCEL_TONE_ID = 868207163582083083
    
class Config:
    VERSION = '1.0.0'
    DEBUG = False
    DISCORD_DEBUG = True
    I18N_LOCALEDIR = 'i18n'
    SERVER_ID = 854646392197611530
    DAILY_ROOM_LIMIT_POWER = 4
    DAILY_ROOM_LIMIT_POWER_PLUS = 8
    LANGS = (
        ('en', 'English', Emoji.ENGLISH_FLAG),
        ('fa', 'Persian', Emoji.PERSIAN_FLAG),
    )
    BRAND_COLOR = 0xA600FF

    IGNORE_MODELS = []

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
        'public_room_button' : {'emoji':868207163993100339 ,'mode':'public', 'i18n':'Public'},
        'private_room_button' : {'emoji':868207164420927497 ,'mode':'private', 'i18n':'Private'},
    }

    ROOM_CONFIRM = {
        'confirm_button' : {'emoji':868207164001497158, 'id':'confirm_button', 'i18n':'Confirm'},
        'again_button' : {'emoji':868207163569471570, 'id':'again_button', 'i18n':'Again'},
        'cancel_button' : {'emoji':868207163582083083, 'id':'cancel_button', 'i18n':'Cancel'},
    }

    ROOM_CLOSE = {'close_button' : {'emoji':868207163582083083,'EN':'Close room','FA':'بستن روم','id':'close_button'}}

class Todoist:
    SECTION_ID = 70057385
    PROJECT_ID = 2278428039

    LABEL_LOW = 2158970441
    LABEL_MEDIUM = 2158970440
    LABEL_HIGH = 2158970439

class Role:
    RAM = 863452008345894912


class Channel:
    TASK_SYSTEM = 866603888559652894
    CREATE_ROOM = 855195507281494056
    
class Category:
    NEW_ROOM = 854682887249330176

class Assets:
    LOGO_PURPLE = 'https://media.discordapp.net/attachments/912750358890160148/912752149090435152/logo_purple.png'
    LOGO_PURPLE_MINI = 'https://media.discordapp.net/attachments/912750358890160148/912752149090435152/logo_purple.png?width=50&height=49'
    TASK_ICON = 'https://media.discordapp.net/attachments/912750358890160148/912752149270777936/task_icon.png'
    ADD_ICON = 'https://media.discordapp.net/attachments/912750358890160148/916057441274318868/plus-circle.png'
    LFG_BANNER = 'https://media.discordapp.net/attachments/912750358890160148/916059487234846830/lfp.png'