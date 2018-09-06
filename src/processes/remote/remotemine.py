
from defs import *  # noqa

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class RemoteMine(CreepProcess):

    def __init__(self, pid, data={}):
        super().__init__('remotemine', pid, 4, data)

    def _run(self):
        self.room = Game.rooms[self._data.room_name]

        print('mining', self._data.mine_room, 'for', self._data.room_name)

        if _.isUndefined(self._data.has_init):
            self.init()

        self.run_creeps()

    def run_creep(self, creep):

        creep.run_current_task()

    def needs_creeps(self):
        if not self._data.has_init:
            return self.has_reserver()

        return len(self._data.creep_names) < self._data.num_sources or self.needs_reserver()

    def has_reserver(self):
        pass

    def needs_reserver(self):
        pass

    def is_valid_creep(self, creep):
        return creep.getActiveBodyparts(WORK) > 0 and creep.getActiveBodyparts(CARRY) < 3

    def gen_body(self, energyAvailable):
        body = [WORK, MOVE]
        mod = [WORK, MOVE]
        total_work = 1

        while self.get_body_cost(body.concat(mod)) <= energyAvailable and total_work < 6:
            total_work += 1
            body = body.concat(mod)

        return body, None

    def init(self):
        mine_room = Game.rooms[self._data.mine_room]
        if _.isUndefined(mine_room):
            return

        self._data.num_sources = len(mine_room.find(FIND_SOURCES))

        self._data.has_init = True
