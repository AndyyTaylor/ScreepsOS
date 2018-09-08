
from defs import *  # noqa

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')
__pragma__('noalias', 'name')


class RemoteMine(CreepProcess):

    def __init__(self, pid, data={}):
        super().__init__('remotemine', pid, 4, data)

    def _run(self):
        self.room = Game.rooms[self._data.room_name]
        self.mine_room = Game.rooms[self._data.mine_room]

        if _.isUndefined(self._data.has_init):
            self.init()

        self.run_creeps()

    def run_creep(self, creep):
        source = Game.getObjectById(self._data.source_id)
        if _.isNull(source):
            creep.moveTo(__new__(RoomPosition(25, 25, self._data.mine_room)))
        elif creep.pos.isNearTo(source):
            creep.harvest(source)
        else:
            creep.moveTo(source)

        creep.run_current_task()

    def needs_creeps(self):
        return len(self._data.creep_names) < 1

    def is_valid_creep(self, creep):
        return creep.getActiveBodyparts(WORK) > 0 and creep.getActiveBodyparts(CARRY) < 3 and \
            not _.isUndefined(creep.memory.remote)

    def gen_body(self, energyAvailable):
        body = [WORK, MOVE]
        mod = [WORK, MOVE]
        total_work = 1

        while self.get_body_cost(body.concat(mod)) <= energyAvailable and total_work < 6:
            total_work += 1
            body = body.concat(mod)

        return body, {'remote': True}

    def init(self):
        mine_room = Game.rooms[self._data.mine_room]
        if _.isUndefined(mine_room):
            return

        self._data.has_init = True
