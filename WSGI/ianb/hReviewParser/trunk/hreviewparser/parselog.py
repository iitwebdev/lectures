import logging

__all__ = ['dummy', 'ParseLog', 'getLevelName']

getLevelName = logging.getLevelName

class ParseLog(object):

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARN = WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    FATAL = logging.FATAL

    def __init__(self):
        self.messages = []

    def log(self, level, msg, *args):
        self.messages.append((level, msg, args))

    def debug(self, msg, *args):
        self.log(self.DEBUG, msg, *args)

    def info(self, msg, *args):
        self.log(self.INFO, msg, *args)

    def warn(self, msg, *args):
        self.log(self.WARN, msg, *args)
    warning = warn

    def error(self, msg, *args):
        self.log(self.ERROR, msg, *args)

    def critical(self, msg, *args):
        self.log(self.CRITICAL, msg, *args)

    def fatal(self, msg, *args):
        self.log(self.FATAL, msg, *args)

    def __str__(self):
        out = []
        for level, msg, args in self.messages:
            level = getLevelName(level)
            level = level + ' '*(8-len(level))
            if args:
                msg = msg % args
            out.append('%s %s' % (level, msg))
        return '\n'.join(out)

class DummyLog(object):

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARN = WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    FATAL = logging.FATAL

    def nothing(*args, **kw):
        pass

    log = debug = info = warn = error = critical = fatal = nothing

dummy = DummyLog()
