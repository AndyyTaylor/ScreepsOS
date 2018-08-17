
from defs import *  # noqa


class Process():

    def __init__(self, name, pid, priority, data={}):
        self.name = name
        self._pid = pid
        self._data = data

        self._killed = False

        self.priority = priority

    def run(self):
        pass

    def is_completed(self):
        if self._killed:
            return True

    def kill(self):
        self._killed = True
