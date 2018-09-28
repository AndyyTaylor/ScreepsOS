
from defs import *  # noqa

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')
__pragma__('noalias', 'name')


class RemoteHaul(CreepProcess):

    def __init__(self, pid, data={}):
        super().__init__('remotehaul', pid, 5, data)

        if pid != -1:
            self.room = Game.rooms[self._data.room_name]
            self.haul_room = Game.rooms[self._data.haul_room]

    def _run(self):
        if _.isUndefined(self._data.has_init):
            self.init()

        self.run_creeps()

    def run_creep(self, creep):
        source = Game.getObjectById(self._data.source_id)
        if creep.is_full():
            creep.set_task("deposit", {'target_id': self.room.storage.id})
        elif creep.is_empty() or creep.is_idle():
            if creep.room.name != self._data.haul_room:
                if not _.isNull(source):
                    creep.moveTo(source)
                else:
                    creep.moveTo(__new__(RoomPosition(25, 25, self._data.haul_room)))
            else:
                creep.set_task("gather")

        if creep.memory.task_name == 'deposit':
            structs = creep.room.find(FIND_STRUCTURES)
            need_repair = _.filter(structs, lambda s: s.hits < s.hitsMax and
                                                      s.structureType != STRUCTURE_WALL and
                                                      s.structureType != STRUCTURE_RAMPART)  # noqa
            if len(need_repair) > 0 and \
                    creep.pos.inRangeTo(creep.pos.findClosestByRange(need_repair), 3):
                creep.repair(creep.pos.findClosestByRange(need_repair))
            elif len(creep.room.construction_sites) > 0:
                target = creep.pos.findClosestByRange(creep.room.construction_sites)
                if creep.pos.inRangeTo(target, 3):
                    creep.build(target)

        creep.run_current_task()

    def needs_creeps(self):
        max_carry = 10 * self._data.path_length * 2 * 1.1 / 50
        total_carry = 0

        for name in self._data.creep_names:
            creep = Game.creeps[name]

            if _.isUndefined(creep):
                continue

            if creep.hits < creep.hitsMax:  # stuffs up calculations
                return False

            total_carry += creep.getActiveBodyparts(CARRY)

        return total_carry < max_carry

    def is_valid_creep(self, creep):
        return creep.getActiveBodyparts(CARRY) > 0 and creep.getActiveBodyparts(WORK) == 1 and \
            not _.isUndefined(creep.memory.remote)

    def gen_body(self, energyAvailable):
        if _.isUndefined(self._data.has_init):
            self.init()

        body = [WORK, CARRY, MOVE]
        mod = [CARRY, CARRY, MOVE]
        total_carry = 1

        max_carry = 10 * self._data.path_length * 2 * 1.1 / 50

        for name in self._data.creep_names:
            creep = Game.creeps[name]
            if _.isUndefined(creep):
                continue

            max_carry -= creep.getActiveBodyparts(CARRY)

        while self.get_body_cost(body.concat(mod)) <= energyAvailable and total_carry < max_carry:
            total_carry += 2
            body = body.concat(mod)

        return body, {'remote': True}

    def init(self):
        haul_room = Game.rooms[self._data.haul_room]
        if _.isUndefined(haul_room):
            return

        source = Game.getObjectById(self._data.source_id)
        start = self.room.storage.pos
        result = PathFinder.search(start, {'pos': source.pos, 'range': 2, 'maxOps': 20000})

        self._data.path_length = len(result.path) + 1

        result = PathFinder.search(source.pos, {'pos': start, 'range': 7})
        if not result.incomplete:
            for tile in result.path:
                if tile.x == 0 or tile.x == 49 or tile.y == 0 or tile.y == 49:
                    continue

                self.ticketer.add_ticket('build', self._pid, {'type': STRUCTURE_ROAD,
                                                              'x': tile.x,
                                                              'y': tile.y,
                                                              'city': tile.roomName
                                                              })

        self._data.has_init = True
