
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

    def _run(self):
        self.room = Game.rooms[self._data.room_name]
        self.vis = self.room.visual

        if _.isUndefined(self._data.has_init):
            self.init()

        self.run_creeps()

    def run_creep(self, creep):
        haul = self._data.sources[creep.memory.haul_ind]

        if creep.is_full():
            creep.set_task('deposit', {'target_id': self.room.storage.id})
        elif creep.is_empty() or creep.is_idle():
            if not _.isNull(haul.cont_id):
                creep.set_task('withdraw', {'target_id': haul.cont_id})
            else:
                creep.set_task('gather')

        creep.run_current_task()

    def needs_creeps(self):
        return len(self._data.creep_names) < len(self._data.sources)

    def is_valid_creep(self, creep):
        return creep.getActiveBodyparts(WORK) < 1 and creep.getActiveBodyparts(CARRY) > 0 \
            and not _.isUndefined(creep.memory.haul_ind)

    def gen_body(self, energyAvailable):
        body = [CARRY, MOVE]
        mod = [CARRY, MOVE]
        total_carry = 1

        indexes = [i for i in range(len(self._data.sources))]
        for name in self._data.creep_names:
            creep = Game.creeps[name]
            if creep and not _.isUndefined(creep.memory.haul_ind):
                indexes.remove(creep.memory.haul_ind)

        haul = self._data.sources[indexes[0]]

        max_carry = haul['bandwidth'] / 50

        while self.get_body_cost(body.concat(mod)) <= energyAvailable and total_carry < max_carry:
            total_carry += 1
            body = body.concat(mod)

        return body, {'haul_ind': indexes[0]}

    def init(self):
        if _.isUndefined(self.room.storage):
            self.kill()
            return

        for source in self.room.sources:
            result = PathFinder.search(self.room.storage.pos, {'pos': source.pos, 'range': 1},
                                       lambda r: self.room.basic_matrix())
            amt = 10
            dist = len(result.path)

            cont_id = None
            structs = self.room.lookForAtArea(LOOK_STRUCTURES, source.pos.y - 1, source.pos.x - 1,
                                              source.pos.y + 1, source.pos.x + 1, True)

            for struct in structs:
                if struct.structure.structureType == STRUCTURE_CONTAINER:
                    cont_id = struct.structure.id
                    break

            self._data.sources.append({'pos': source.pos, 'cont_id': cont_id,
                                       'bandwidth': amt * dist * 2 * 1.2})

        self._data.has_init = True
