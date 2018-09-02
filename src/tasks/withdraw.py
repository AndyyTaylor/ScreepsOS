
from defs import *  # noqa

from framework.task import Task


class Withdraw(Task):

    def __init__(self, data={}):
        super().__init__('withdraw', data)

    def _run(self, creep):
        target = Game.getObjectById(self._data.target_id)
        if not target or _.sum(target.store) == 0:
            return

        if not creep.pos.isNearTo(target):
            creep.moveTo(target)
        else:
            creep.withdraw(target, RESOURCE_ENERGY)

    def is_completed(self, creep):
        target = Game.getObjectById(self._data.target_id)

        return creep.is_full() or not target or _.sum(target.store) == 0
