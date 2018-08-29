
from defs import *  # noqa

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class BuildSite(CreepProcess):

    def __init__(self, pid, data={}):
        super().__init__('buildsite', pid, 4, data)

    def _run(self):
        self.room = Game.rooms[self._data.room_name]
        self.controller = self.room.controller

        self.place_flag()
        self.run_creeps()

    def run_creep(self, creep):
        if creep.is_empty():
            creep.set_task('gather')
        elif creep.is_full() or creep.is_idle():
            creep.set_task('build', {'site_id': self._data.site_id})

        creep.run_current_task()

    def needs_creeps(self):
        return len(self._data.creep_names) < 1  # Scale this

    def place_flag(self):
        flags = self.room.flags

        site = Game.getObjectById(self._data.site_id)
        if not site:
            return

        x, y = site.pos.x, site.pos.y

        already_placed = False
        for flag in flags:
            if flag['name'] == 'BuildSite(' + str(self._data.room_name) + ')':
                if flag['pos']['x'] == x and flag['pos']['y'] == y:
                    already_placed = True
                    break
                else:
                    flag.remove()

        if not already_placed:
            self.room.createFlag(x, y, 'BuildSite(' + str(self._data.room_name) + ')', COLOR_ORANGE)
