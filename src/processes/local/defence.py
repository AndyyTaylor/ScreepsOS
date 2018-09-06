
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
        repairs = _.filter(self.room.find(FIND_STRUCTURES),
                           lambda s: s.hits < s.hitsMax * js_global.TOWER_REPAIR)

        for tower in self.room.towers:
            if len(hostile_creeps) > 0:
                tower.attack(hostile_creeps[0])
            elif len(repairs) > 0:
                tower.repair(repairs[0])
