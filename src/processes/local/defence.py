
from defs import *  # noqa

from framework.process import Process

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class Defence(Process):

    def __init__(self, pid, data={}):
        super().__init__('defence', pid, 2, data)

    def _run(self):
        self.room = Game.rooms[self._data.room_name]
        self.vis = self.room.visual

        hostile_creeps = self.room.find(FIND_HOSTILE_CREEPS)

        if len(hostile_creeps) > 0:
            for tower in self.room.towers:
                tower.attack(hostile_creeps[0])
