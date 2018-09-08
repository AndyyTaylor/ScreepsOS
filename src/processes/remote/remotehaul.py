
from defs import *  # noqa

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')
__pragma__('noalias', 'name')


class RemoteHaul(CreepProcess):

    def __init__(self, pid, data={}):
        super().__init__('remotehaul', pid, 4, data)

        if pid != -1:
            self.room = Game.rooms[self._data.room_name]
            self.haul_room = Game.rooms[self._data.haul_room]

    def _run(self):
        print('remote hauling', self._data.haul_room)
        if _.isUndefined(self._data.has_init):
            self.init()

        self.run_creeps()

    def run_creep(self, creep):
        source = Game.getObjectById(self._data.source_id)
        if _.isNull(source):
            creep.moveTo(__new__(RoomPosition(25, 25, self._data.haul_room)))
        else:
            creep.moveTo(source)

        creep.run_current_task()

    def needs_creeps(self):
        return len(self._data.creep_names) < 0

    def is_valid_creep(self, creep):
        return creep.getActiveBodyparts(CARRY) > 0 and creep.getActiveBodyparts(WORK) == 1 and \
            not _.isUndefined(creep.memory.remote)

    def gen_body(self, energyAvailable):
        body = [WORK, MOVE, CARRY, MOVE]
        mod = [CARRY, MOVE]
        total_carry = 1

        max_carry = 10 * self._data.path_length * 2 / 50

        while self.get_body_cost(body.concat(mod)) <= energyAvailable and total_carry < max_carry:
            total_carry += 1
            body = body.concat(mod)

        return body, {'remote': True}

    def init(self):
        haul_room = Game.rooms[self._data.haul_room]
        if _.isUndefined(haul_room):
            return

        source = Game.getObjectById(self._data.source_id)
        start = self.room.storage.pos
        result = PathFinder.search(start, {'pos': source.pos, 'range': 1})

        self._data.path_length = len(result.path)

        self._data.has_init = True
