
from defs import *  # noqa

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class Logistics(CreepProcess):

    def __init__(self, pid, data={}):
        super().__init__('logistics', pid, 2, data)

        if _.isUndefined(self._data.sources):
            self._data.sources = []

        if _.isUndefined(self._data.sinks):
            self._data.sinks = []

        if pid != -1:
            self.room = Game.rooms[self._data.room_name]
            self.vis = self.room.visual

    def _run(self):
        if _.isUndefined(self._data.has_init):
            self.init()

        self.run_creeps()

    def run_creep(self, creep):
        haul = self._data.sources[creep.memory.haul_ind]
        if _.isUndefined(haul):  # Sources / sinks has changed
            creep.suicide()
            return

        cont = Game.getObjectById(haul.cont_id)
        if creep.is_full():
            creep.set_task('deposit', {'target_id': self.room.storage.id})
            Memory.stats.rooms[self._data.room_name].lharvest.transfer += creep.carry.energy
        elif creep.is_empty() or creep.is_idle():
            if not _.isNull(cont) and _.sum(cont.store) > 100:
                creep.set_task('withdraw', {'target_id': haul.cont_id})
            else:
                creep.set_task('gather')

        creep.run_current_task()

    def needs_creeps(self):
        return len(self._data.creep_names) < len(self._data.sources)

    def is_valid_creep(self, creep):
        return creep.memory.role == 'hauler'

    def gen_body(self, energyAvailable):
        if self.room.rcl < 5:  # Should check path cost
            body = [CARRY, MOVE]
            mod = [CARRY, MOVE]
            total_carry = 1
            carry_mod = 1
        else:
            body = [CARRY, CARRY, MOVE]
            mod = [CARRY, CARRY, MOVE]
            total_carry = 2
            carry_mod = 2

        indexes = [i for i in range(len(self._data.sources))]
        for name in self._data.creep_names:
            creep = Game.creeps[name]
            if creep and not _.isUndefined(creep.memory.haul_ind):
                if indexes.includes(creep.memory.haul_ind):
                    indexes.remove(creep.memory.haul_ind)

        haul = self._data.sources[indexes[0]]

        max_carry = haul['bandwidth'] / 50

        while self.get_body_cost(body.concat(mod)) <= energyAvailable and total_carry < max_carry:
            total_carry += carry_mod
            body = body.concat(mod)

        return body, {'haul_ind': indexes[0], 'role': 'hauler'}

    def init(self):
        if _.isUndefined(self.room.storage):
            self.kill()
            return

        self.load_sources()  # like room sources..
        if self.room.rcl >= 6:
            self.load_mineral()

        self._data.has_init = True

    def load_sources(self):
        for source in self.room.sources:
            result = PathFinder.search(self.room.storage.pos, {'pos': source.pos, 'range': 1},
                                       lambda r: self.room.basic_matrix())
            amt = 10
            dist = len(result.path)

            cont_id = None  # 2 for links, but be careful of sources near controllers
            structs = self.room.lookForAtArea(LOOK_STRUCTURES, source.pos.y - 2, source.pos.x - 2,
                                              source.pos.y + 2, source.pos.x + 2, True)

            has_link = False
            for struct in structs:
                if struct.structure.structureType == STRUCTURE_LINK:
                    has_link = True
                    break
                elif struct.structure.structureType == STRUCTURE_CONTAINER:
                    cont_id = struct.structure.id
                    break  # Cont will be removed upon link construction

            if has_link:
                continue  # Don't add as we don't need hauler

            self._data.sources.append({'pos': source.pos, 'cont_id': cont_id,
                                       'bandwidth': amt * dist * 2 * 1.2})

    def load_mineral(self):
        mineral = self.room.mineral
        result = PathFinder.search(self.room.center, {'pos': mineral.pos, 'range': 1},
                                   lambda r: self.room.basic_matrix())
        amt = 3
        dist = len(result.path)

        cont_id = None
        structs = self.room.lookForAtArea(LOOK_STRUCTURES, mineral.pos.y - 1, mineral.pos.x - 1,
                                          mineral.pos.y + 1, mineral.pos.x + 1, True)
        for struct in structs:
            if struct.structure.structureType == STRUCTURE_CONTAINER:
                cont_id = struct.structure.id
                break  # Cont will be removed upon link construction

        self._data.sources.append({'pos': mineral.pos, 'cont_id': cont_id,
                                   'bandwidth': amt * dist * 2 * 1.2})
