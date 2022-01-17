import gettext
import os
from gettext import GNUTranslations, translation

from data.config import Config

__all__ = ['i18n']

class i18n:
    
    def __init__(self, lang: str = 'en') -> None:
        self.locale_dir = Config.I18N_LOCALEDIR
        self.domain = Config.I18N_DOMAIN
        self.lang = lang
        self._install()
    
    def _install(self):
        translate = gettext.translation(domain=self.domain, localedir=self.locale_dir, languages=[self.lang], fallback=True)
        if isinstance(translate, GNUTranslations):
            translate.install()
            self.translate = translate
    
    def change_lang(self, lang: str) -> None:
        self.lang = lang
        self._install()

    @property
    def info(self):
        return self.translate.info()
    
    @property
    def gettext(self):
        return self.translate.gettext

    @property
    def ngettext(self):
        return self.translate.ngettext

    @property
    def pgettext(self):
        return self.translate.pgettext

    def __str__(self) -> str:
        return f'<lang={self.lang} domain={self.domain}>'

    def __repr__(self):
        return f'<lang={self.lang} domain={self.domain} localedir={self.locale_dir}>'

    @property
    @staticmethod
    def active_langs():
        list = []
        for lang in os.listdir(Config.I18N_LOCALEDIR):
            if lang != 'pot':
                list.append(lang)
        return list