
from defs import *  # noqa

from framework.task import Task


class Deposit(Task):

    def __init__(self, data={}):
        super().__init__('deposit', data)

    def _run(self, creep):
        target = Game.getObjectById(self._data.target_id)
        if not target or _.sum(target.store) == target.storeCapacity:
            return

        if not creep.pos.isNearTo(target):
            creep.moveTo(target)
        else:
            creep.transfer(target, RESOURCE_ENERGY)

    def is_completed(self, creep):
        target = Game.getObjectById(self._data.target_id)

        return creep.is_empty() or not target or _.sum(target.store) == target.storeCapacity
