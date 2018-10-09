
from defs import *  # noqa

from framework.task import Task

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class Withdraw(Task):

    def __init__(self, data=None):
        super().__init__('withdraw', data)

    def _run(self, creep):
        target = Game.getObjectById(self._data.target_id)
        if not target or (not _.isUndefined(target.store) and _.sum(target.store) == 0) or \
                         (not _.isUndefined(target.energy) and target.energy == 0):
            return

        if not creep.pos.isNearTo(target):
            creep.moveTo(target)
        else:
            type = RESOURCE_ENERGY
            if not _.isUndefined(self._data['type']):
                type = self._data['type']
            elif not _.isUndefined(target.store):
                type = Object.keys(target.store).pop()
            creep.withdraw(target, type)

    def is_completed(self, creep):
        target = Game.getObjectById(self._data.target_id)

        if not target:
            return True

        type = RESOURCE_ENERGY
        if not _.isUndefined(self._data['type']):
            type = self._data['type']
        elif not _.isUndefined(target.store):
            type = Object.keys(target.store).pop()

        return creep.is_full() or \
            (not _.isUndefined(target.store) and target.store[type] == 0) or \
            (not _.isUndefined(target.energy) and target.energy == 0)
