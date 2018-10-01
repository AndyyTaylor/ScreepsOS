
from defs import *  # noqa

from framework.task import Task

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


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
            type = RESOURCE_ENERGY
            if not _.isUndefined(self._data.type):
                type = self._data.type
            elif not _.isUndefined(target.store):
                type = Object.keys(creep.carry).pop()

            if not _.isUndefined(creep.memory.role) and creep.memory.role == 'rhauler':
                Memory.stats.rooms[creep.memory.city].rharvest.transfer += creep.carry.energy

            creep.transfer(target, type)

    def is_completed(self, creep):
        target = Game.getObjectById(self._data.target_id)

        return creep.is_empty() or not target or _.sum(target.store) == target.storeCapacity
