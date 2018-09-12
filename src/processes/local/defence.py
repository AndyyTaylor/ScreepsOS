
from defs import *  # noqa

from framework.process import Process

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class Defence(Process):

    def __init__(self, pid, data={}):
        super().__init__('defence', pid, 0, data)

        if pid != -1:
            self.room = Game.rooms[self._data.room_name]
            self.vis = self.room.visual

            self.validate_memory()

    def _run(self):
        hostile_creeps = self.room.find(FIND_HOSTILE_CREEPS)
        injured = _.filter(self.room.find(FIND_MY_CREEPS), lambda c: c.hits < c.hitsMax)
        repairs = _.filter(self.room.find(FIND_STRUCTURES),
                           lambda s: s.hits < s.hitsMax * js_global.TOWER_REPAIR)

        for tower in self.room.towers:
            if len(hostile_creeps) > 0:
                target = tower.pos.findClosestByRange(hostile_creeps)
                tower.attack(target)
                self.room.memory.towers.attack += 10
            elif len(injured) > 0:
                target = tower.pos.findClosestByRange(injured)
                tower.heal(target)
                self.room.memory.towers.heal += 10
            elif len(repairs) > 0:
                tower.repair(repairs[0])
                self.room.memory.towers.repair += 10

    def validate_memory(self):
        if _.isUndefined(self.room.memory):
            self.room.memory = {}

        if _.isUndefined(self.room.memory.towers):
            self.room.memory.towers = {}

        if _.isUndefined(self.room.memory.towers.attack):
            self.room.memory.towers.attack = 0

        if _.isUndefined(self.room.memory.towers.repair):
            self.room.memory.towers.repair = 0

        if _.isUndefined(self.room.memory.towers.heal):
            self.room.memory.towers.heal = 0
