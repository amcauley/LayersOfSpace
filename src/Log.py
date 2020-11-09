import logging
import sys

class _Log:
    instance = None

    @staticmethod
    def getInstance():
        return _Log.instance if _Log.instance else _Log()

    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.handler = logging.StreamHandler(sys.stdout)
        self.handler.setLevel(logging.DEBUG)
        self.logger.addHandler(self.handler)

        self.debug('Initialized logger')

    def debug(self, s):
        self.logger.debug(s)

    def info(self, s):
        return self.logger.info(s)

    def warning(self, s):
        return self.logger.warning(s)

Log = _Log()
