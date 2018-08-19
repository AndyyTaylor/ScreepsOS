
from defs import *  # noqa

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class UpgradeSite(CreepProcess):

    def __init__(self, pid, data={}):
        super().__init__('upggradesite', pid, 5, data)

    def _run(self):
        self.room = Game.rooms[self._data.room_name]
        self.controller = self.room.controller

        if _.isUndefined(self._data.has_init):
            self.init()

        self.place_flag()

        self.run_creeps()

    def run_creeps(self):
        expired_creeps = []
        for name in self._data.creep_names:
            creep = Game.creeps[name]

            if not creep:
                expired_creeps.append(name)
                continue

            self.run_creep(creep)

        for name in expired_creeps:
            self._data.creep_names.remove(name)

    def run_creep(self, creep):
        if creep.is_empty():
            creep.set_task('gather')
        elif creep.is_full() or creep.is_idle():
            creep.set_task('upgrade')

        creep.run_current_task()

    def needs_creeps(self):
        return len(self._data.creep_names) < 2  # Scale this

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
