
from defs import *  # noqa

from framework.task import Task


class Travel(Task):

    def __init__(self, data={}):
        super().__init__('travel', data)

        if _.isUndefined(self._data.distance):
            self._data.distance = 0

    def _run(self, creep):
        dest = __new__(RoomPosition(self._data.dest_x, self._data.dest_y,
                                    self._data.dest_room_name))

        if not creep.pos.getRangeTo(dest) <= self._data.distance:
            creep.moveTo(dest)
        else:
            self._data.completed = True

    def is_completed(self, creep):
        return self._data.completed
