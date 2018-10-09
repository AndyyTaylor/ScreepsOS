
from defs import *  # noqa

from framework.task import Task


class Gather(Task):

    def __init__(self, data=None):
        super().__init__('gather', data)

    def _run(self, creep):
        target = Game.getObjectById(self._data.target_id)
        if not target or (not _.isUndefined(target.store) and target.store[RESOURCE_ENERGY] == 0):
            target = self.select_target(creep, creep.room)

            if not target:
                self._data.completed = True
                return

            self._data.target_id = target.id

        if not creep.pos.isNearTo(target):
            creep.moveTo(target)
        else:
            if not _.isUndefined(target.resourceType):
                creep.pickup(target)
            else:
                creep.withdraw(target, RESOURCE_ENERGY)

    def select_target(self, creep, room):
        energy = _.filter(room.find(FIND_DROPPED_RESOURCES),
                          lambda r: r.resourceType == RESOURCE_ENERGY and r.amount > 50)
        tombstones = _.filter(room.tombstones, lambda t: t.store[RESOURCE_ENERGY] > 50)

        if len(energy) > 0:
            target = creep.pos.findClosestByRange(energy)
        elif len(tombstones) > 0:
            target = creep.pos.findClosestByRange(tombstones)
        else:
            return

        return target

    def is_completed(self, creep):
        return creep.is_full() or self._data.completed
