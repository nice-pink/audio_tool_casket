from enum import Enum

class Log:

    class Type(Enum):
        NoLog = 0
        Error = 1
        Warning = 2
        Info = 3
        All = 4

    LOG_LEVEL = Type.All

    @staticmethod
    def error(*args, **kwargs):
        if Log.LOG_LEVEL.value >= Log.Type.Error.value:
            print( "\033[1;31m" + " ".join(map(str,args)), **kwargs)

    @staticmethod
    def warning(*args, **kwargs):
        if Log.LOG_LEVEL.value >= Log.Type.Warning.value:
            print( "\033[1;33m" + " ".join(map(str,args)), **kwargs)

    @staticmethod
    def info(*args, **kwargs):
        if Log.LOG_LEVEL.value >= Log.Type.Info.value:
            print( "\033[0m" + " ".join(map(str,args)), **kwargs)

    @staticmethod
    def happy(*args, **kwargs):
        if Log.LOG_LEVEL.value >= Log.Type.Info.value:
            print( "\033[1;32m" + " ".join(map(str,args)), **kwargs)
