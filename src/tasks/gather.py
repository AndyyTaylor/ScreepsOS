
from defs import *  # noqa

from framework.task import Task


class Gather(Task):

    def __init__(self, data={}):
        super().__init__('gather', data)

    def _run(self, creep):
        target = Game.getObjectById(self._data.target_id)
        if not target:
            target = self.select_target(creep, creep.room)

            if not target:
                self._data.completed = True
                return

            self._data.target_id = target.id

        if not creep.pos.isNearTo(target):
            creep.moveTo(target)
        else:
            creep.pickup(target)

    def select_target(self, creep, room):
        energy = _.filter(room.find(FIND_DROPPED_RESOURCES),
                          lambda r: r.resourceType == RESOURCE_ENERGY and r.amount > 50)

        if not energy:
            return

        target = creep.pos.findClosestByRange(energy)

        return target

    def is_completed(self, creep):
        return creep.is_full() or self._data.completed
