
from defs import *  # noqa


class Task():

    def __init__(self, name, data={}):
        self.name = name
        self._data = data

    def run(self, creep):
        print("Task running with", creep['name'])
