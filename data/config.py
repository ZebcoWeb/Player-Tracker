


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