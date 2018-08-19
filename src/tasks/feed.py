
from defs import *  # noqa

from framework.task import Task


class Feed(Task):

    def __init__(self, data={}):
        super().__init__('feed', data)

    def _run(self, creep):
        target = Game.getObjectById(self._data.target_id)
        if not target:
            target = self.select_target(creep, creep.room)

            if not target:
                creep.say("No feed")
                return

            self._data.target_id = target.id

        if not creep.pos.isNearTo(target):
            creep.moveTo(target)
        else:
            creep.transfer(target, RESOURCE_ENERGY)

    def select_target(self, creep, room):
        locations = _.filter(room.feed_locations,
                             lambda s: s.energy < s.energyCapacity)

        if not locations:
            return

        target = creep.pos.findClosestByRange(locations)

        return target

    def is_completed(self, creep):
        return creep.is_empty()
