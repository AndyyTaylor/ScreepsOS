
from defs import *  # noqa

from framework.task import Task


class Travel(Task):

    def __init__(self, data={}):
        super().__init__('travel', data)

    def _run(self, creep):
        dest = __new__(RoomPosition(self._data.dest_x, self._data.dest_y,
                                    self._data.dest_room_name))

        if not creep.pos.isNearTo(dest):
            creep.moveTo(dest)
        else:
            self._data.completed = True

    def is_completed(self, creep):
        return self._data.completed
