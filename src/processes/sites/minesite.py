
from defs import *  # noqa

from framework.process import Process


class MineSite(Process):

    def __init__(self, pid, data={}):
        super().__init__("minesite", pid, 5, data)

    def run(self):
        pass
