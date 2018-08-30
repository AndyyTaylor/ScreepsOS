
from defs import *  # noqa

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class UpgradeSite(CreepProcess):

    def __init__(self, pid, data={}):
        super().__init__('upggradesite', pid, 5, data)

        if pid != -1:
            self.room = Game.rooms[self._data.room_name]
            self.controller = self.room.controller

    def _run(self):
        if _.isUndefined(self._data.has_init):
            self.init()

        self.place_flag()

        self.run_creeps()

    def run_creep(self, creep):
        if creep.is_empty():
            creep.set_task('gather')
        elif creep.is_full() or creep.is_idle():
            creep.set_task('upgrade')

        creep.run_current_task()

    def needs_creeps(self):
        if len(self.room.construction_sites):
            return len(self._data.creep_names) < 1  # Scale this
        else:
            return len(self._data.creep_names) < 3

    def is_valid_creep(self, creep):
        return creep.getActiveBodyparts(WORK) > 0 and creep.getActiveBodyparts(CARRY) > 0

    def gen_body(self, energy):
        body = [WORK, CARRY, MOVE]
        mod = [WORK, CARRY, MOVE]

        while self.get_body_cost(body.concat(mod)) <= energy:
            body = body.concat(mod)

        return body

    def init(self):  # This should request certain buildings. container / link etc
        self._data.has_init = True

        # Will identify the upcont for use

    def place_flag(self):
        flags = self.room.flags

        x, y = self.controller.pos.x, self.controller.pos.y

        already_placed = False
        for flag in flags:
            if flag['name'] == 'UpgradeSite(' + str(self._data.room_name) + ')':
                already_placed = True
                break

        if not already_placed:
            self.room.createFlag(x, y, 'UpgradeSite(' + str(self._data.room_name) + ')', COLOR_BLUE)
