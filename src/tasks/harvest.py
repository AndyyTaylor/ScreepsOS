
from defs import *  # noqa

from framework.task import Task


class Harvest(Task):

    def __init__(self, data={}):
        super().__init__('harvest', data)

    def _run(self, creep):
        source = Game.getObjectById(self._data.source_id)

        if creep.pos.isNearTo(source):
            creep.harvest(source)
        else:
            creep.moveTo(source)
