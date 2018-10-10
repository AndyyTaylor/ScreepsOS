
from defs import *  # noqa


class Task():

    def __init__(self, name, data=None):
        if data is None:
            data = {}

        self.name = name
        self._data = data

    def run(self, creep):
        self._run(creep)

        if self.is_completed(creep):
            creep.clear_task()

    def is_completed(self, creep):
        return False
