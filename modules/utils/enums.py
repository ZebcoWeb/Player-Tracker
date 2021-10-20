from enum import Enum


__all__ = ['LogType']


class LogType(Enum):

    Cache = 'CATCH'
    Database = 'DATABASE'
    PT = 'PLAYER-TRACKER'
    Env = 'ENV'
    Yaml = 'YAML'
    Discord = 'DISCORD'
    Test = 'TEST'