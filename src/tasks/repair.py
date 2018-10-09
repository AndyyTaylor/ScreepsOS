
from defs import *  # noqa

from framework.task import Task


class Repair(Task):

    def __init__(self, data=None):
        super().__init__('repair', data)

    def _run(self, creep):
        target = Game.getObjectById(self._data.site_id)
        if not target or target.hits == target.hitsMax:
            self._data.completed = True
            return

        if not creep.pos.inRangeTo(target, 3):
            creep.moveTo(target)
        else:
            creep.repair(target)

    def is_completed(self, creep):
        return creep.is_empty() or self._data.completed
