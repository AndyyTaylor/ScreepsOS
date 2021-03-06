
from defs import *  # noqa

from framework.process import Process

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class Defence(Process):

    def __init__(self, pid, data={}):
        super().__init__('defence', pid, 3, data)

        if pid != -1:
            self.room = Game.rooms[self._data.room_name]
            self.vis = self.room.visual

            self.validate_memory()

    def _run(self):
        hostile_creeps = self.room.hostile_military
        injured = _.filter(self.room.find(FIND_MY_CREEPS), lambda c: c.hits < c.hitsMax)
        repairs = _.filter(self.room.find(FIND_STRUCTURES),
                           lambda s:
                           (s.hits < s.hitsMax * js_global.TOWER_REPAIR and
                           s.structureType != STRUCTURE_RAMPART and s.structureType != STRUCTURE_WALL) or
                           (s.structureType == STRUCTURE_RAMPART and s.hits < self.room.memory.walls.hits / 2))

        for tower in self.room.towers:
            if len(hostile_creeps) > 0:
                target = tower.pos.findClosestByRange(hostile_creeps)
                tower.attack(target)
                self.room.memory.towers.attack += 10
            elif len(injured) > 0:
                target = tower.pos.findClosestByRange(injured)
                tower.heal(target)
                self.room.memory.towers.heal += 10
            elif len(repairs) > 0 and tower.energy > 500:
                tower.repair(repairs[0])
                self.room.memory.towers.repair += 10

        for spawn in self.room.spawns:
            if spawn.hits < spawn.hitsMax * 0.5:
                self.room.controller.activateSafeMode()

        for name in self._data.remotes:
            room = Game.rooms[name]
            if _.isUndefined(room):
                continue

            if _.isUndefined(room.memory):
                room.memory = {}

            if _.isUndefined(room.memory.threats):
                room.memory.threats = {}

            room.memory.threats.count = len(room.hostile_military)

            max_ticks = 0
            for creep in room.hostile_military:
                max_ticks = max(creep.ticksToLive, max_ticks)

            room.memory.threats.safe_tick = Game.time + max_ticks

        for name in self._data.remotes:
            if _.isUndefined(Memory.rooms[name]) or _.isUndefined(Memory.rooms[name].threats):
                continue

            if Memory.rooms[name].threats.safe_tick > Game.time:
                if self.scheduler.count_by_name('remoteinvaderdefence', self._pid) < 1 and \
                        Memory.rooms[name].threats.count < 2:
                    self.launch_child_process('remoteinvaderdefence', {'room_name': self._data.room_name,
                                                                       'target_room': name})

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
