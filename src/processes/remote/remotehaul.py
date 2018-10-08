
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
        if _.sum(creep.carry) >= creep.carryCapacity - 2:  # for repair
            creep.set_task("deposit", {'target_id': self.room.storage.id})
        elif creep.is_empty() or creep.is_idle():
            cont = Game.getObjectById(self._data.deposit_id)
            creep.say(cont)
            if not _.isNull(cont):
                creep.set_task('withdraw', {'target_id': cont.id})
            elif creep.room.name != self._data.haul_room:
                if not _.isNull(source):
                    creep.moveTo(source)
                else:
                    creep.moveTo(__new__(RoomPosition(25, 25, self._data.haul_room)))
            else:
                creep.set_task("gather")

        if creep.carry.energy > 0:
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

    def _needs_creeps(self, creep_names):
        max_carry = 10 * self._data.path_length * 2 * 1.2 / 50
        total_carry = 0

        for name in creep_names:
            creep = Game.creeps[name]

            if _.isUndefined(creep):
                continue

            if creep.hits < creep.hitsMax:  # stuffs up calculations
                return False

            total_carry += creep.getActiveBodyparts(CARRY)

        return total_carry < max_carry

    def is_valid_creep(self, creep):
        return creep.memory.role == 'rhauler'

    def _gen_body(self, energyAvailable, creep_names):
        if _.isUndefined(self._data.has_init):
            self.init()

        body = [WORK, CARRY, MOVE]
        mod = [CARRY, CARRY, MOVE]
        total_carry = 1

        max_carry = 10 * self._data.path_length * 2 * 1.2 / 50
        current_carry = []

        for name in creep_names:
            creep = Game.creeps[name]
            if _.isUndefined(creep):
                continue

            max_carry -= creep.getActiveBodyparts(CARRY)
            current_carry.append(creep.getActiveBodyparts(CARRY))

        while len(current_carry) > 0 and max_carry + min(current_carry) < 50:
            max_carry += min(current_carry)
            current_carry.remove(min(current_carry))

        while self.get_body_cost(body.concat(mod)) <= energyAvailable \
                and total_carry < max_carry and len(body.concat(mod)) <= 50:
            total_carry += 2
            body = body.concat(mod)

        Memory.stats.rooms[self._data.room_name].rharvest.spawn += self.get_body_cost(body)

        return body, {'remote': True, 'role': 'rhauler'}

    def init(self):
        haul_room = Game.rooms[self._data.haul_room]
        if _.isUndefined(haul_room):
            return

        source = Game.getObjectById(self._data.source_id)
        start = self.room.storage.pos
        result = PathFinder.search(start, {'pos': source.pos, 'range': 2, 'maxOps': 20000})

        self._data.path_length = len(result.path) + 1

        self._data.deposit_id = self.load_deposit(source)

        result = PathFinder.search(source.pos, {'pos': start, 'range': 7, 'maxOps': 20000})
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

    def load_deposit(self, source):
        deposit_id = None
        x, y = source.pos.x, source.pos.y
        nearby_structs = self.haul_room.lookForAtArea(LOOK_STRUCTURES, y - 1, x - 1, y + 1, x + 1, True)
        for struct in nearby_structs:
            if struct.structure.structureType == STRUCTURE_CONTAINER:
                deposit_id = struct.structure.id
                break

        return deposit_id
