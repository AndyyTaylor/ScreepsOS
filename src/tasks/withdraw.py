
from defs import *  # noqa

from framework.task import Task

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class Withdraw(Task):

    def __init__(self, data={}):
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

        return creep.is_full() or not target or _.sum(target.store) == 0
