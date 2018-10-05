
from defs import *  # noqa

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')
__pragma__('noalias', 'name')


class SappAttack(CreepProcess):

    def __init__(self, pid, data={}):
        super().__init__('sappattack', pid, 5, data)

        if _.isUndefined(self._data.military):
            self._data.military = True

        if self._pid != -1:
            self.room = Game.rooms[self._data.room_name]

    def _run(self):
        self.target_room = Game.rooms[self._data.target_room]

        self.run_creeps()

    def roomCallback(self, name):
        room = Game.rooms[name]

        if _.isUndefined(room):
            return

        costs = __new__(PathFinder.CostMatrix)

        for struct in room.find(FIND_STRUCTURES):
            if struct.structureType == STRUCTURE_ROAD:
                costs.set(struct.pos.x, struct.pos.y, 1)
            elif (struct.structureType != STRUCTURE_CONTAINER and
                    (struct.structureType != STRUCTURE_RAMPART or
                     not struct.my)):
                costs.set(struct.pos.x, struct.pos.y, 0xff)

        for creep in room.find(FIND_CREEPS):
            costs.set(creep.pos.x, creep.pos.y, 0xff)

        return costs

    def run_creep(self, creep):
        if _.isUndefined(creep.memory.attacking) or creep.hits == creep.hitsMax:
            creep.memory.attacking = True
        elif creep.getActiveBodyparts(TOUGH) == 0:
            creep.memory.attacking = False

        if creep.memory.attacking:
            creep.rangedMassAttack()

            if creep.room.name != self._data.target_room or creep.pos.x > 48 or creep.pos.x < 2 or \
                    creep.pos.y > 48 or creep.pos.y < 2:

                if _.isUndefined(self._data.path) or Game.time % 20 == 0:
                    start = __new__(RoomPosition(25, 25, self._data.target_room))
                    result = PathFinder.search(creep.pos, {'pos': start, 'range': 23},
                                               {'maxOps': 5000,
                                                'roomCallback': lambda r: self.roomCallback(r)})

                    self._data.path = result.path

                result = creep.moveByPath(self._data.path)

                if result == ERR_NOT_FOUND:
                    start = __new__(RoomPosition(25, 25, self._data.target_room))
                    result = PathFinder.search(creep.pos, {'pos': start, 'range': 23},
                                               {'maxOps': 5000,
                                                'roomCallback': lambda r: self.roomCallback(r)})

                    self._data.path = result.path

                # creep.moveTo(__new__(RoomPosition(25, 25, self._data.target_room)))

        else:
            if creep.room.name == self._data.target_room or creep.pos.x > 47 or creep.pos.x < 3 or \
                    creep.pos.y > 47 or creep.pos.y < 3:
                creep.moveTo(self.room.controller)

        creep.heal(creep)

    def needs_creeps(self):
        # if Game.time < 9418045 + 1000:
        return len(self._data.creep_names) < 1
        # else:
        #     return False

    def is_valid_creep(self, creep):
        return creep.memory.role == 'sapper'

    def gen_body(self, energy):
        body = [MOVE, RANGED_ATTACK, MOVE, HEAL]
        mod = [TOUGH, MOVE]
        tough_count = 1

        while self.get_body_cost(body.concat(mod)) <= energy and len(body.concat(mod)) <= 50:
            body = body.concat(mod)
            tough_count += 1  # will count ranged attack after

            if tough_count >= 10:
                mod = [HEAL, MOVE]

        return body, {'role': 'sapper'}
