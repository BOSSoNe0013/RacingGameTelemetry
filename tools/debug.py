from enum import Enum


class LogLevel(Enum):
    error = 0
    warn = 1
    verbose = 2

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented


class TextBlock:
    HEADER = '\033[95m'
    OK_BLUE = '\033[94m'
    OK_GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END_C = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    NO_CURSOR = '\033[?25l'
    CURSOR = '\033[?25h'
    SHADE_BLOCK = '\342\226\222'

    def __init__(self):
        pass


DEBUG = False
LEVEL = LogLevel.error


class Debug:
    def __init__(self):
        pass

    @staticmethod
    def set_log_level(level):
        global LEVEL
        LEVEL = level

    @staticmethod
    def get_log_level():
        global LEVEL
        return LEVEL

    @staticmethod
    def toggle(state):
        global DEBUG
        DEBUG = state

    @staticmethod
    def err(msg):
        print('%sERROR: %s%s' % (TextBlock.FAIL, msg, TextBlock.END_C))

    @staticmethod
    def warn(msg):
        if DEBUG and LEVEL >= LogLevel.warn:
            print('%sWARN: %s%s' % (TextBlock.WARNING, msg, TextBlock.END_C))

    @staticmethod
    def notice(msg):
        if DEBUG and LEVEL >= LogLevel.verbose:
            print('%sNOTICE: %s%s' % (TextBlock.WARNING, msg, TextBlock.END_C))

    @staticmethod
    def log(msg, tag=None):
        if DEBUG and LEVEL >= LogLevel.verbose:
            if tag is None:
                print(msg)
            else:
                print('%s%s%s: %s' % (TextBlock.BOLD, tag, TextBlock.END_C, msg))

    @staticmethod
    def ok(msg):
        if DEBUG and LEVEL >= LogLevel.verbose:
            print('%s%s%s' % (TextBlock.OK_GREEN, msg, TextBlock.END_C))

    @staticmethod
    def ko(msg):
        if DEBUG and LEVEL >= LogLevel.verbose:
            print('%s%s%s' % (TextBlock.FAIL, msg, TextBlock.END_C))

    @staticmethod
    def head(msg):
        if DEBUG and LEVEL >= LogLevel.verbose:
            print('%s%s%s' % (TextBlock.OK_BLUE, msg, TextBlock.END_C))
