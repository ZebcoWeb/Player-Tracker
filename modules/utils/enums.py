from enum import Enum


__all__ = ['LogType']


class EnumBase(Enum):
    # return value
    def __str__(self):
        return self.value



class LogType(EnumBase):

    Cache = 'CATCH'
    Database = 'DATABASE'
    PT = 'PLAYER-TRACKER'
    Env = 'ENV'
    Yaml = 'YAML'
    Discord = 'DISCORD'
    Test = 'TEST'


print(LogType.Cache)