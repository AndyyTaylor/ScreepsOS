
from defs import *  # noqa

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class RepairSite(CreepProcess):

    def __init__(self, pid, data={}):
        super().__init__('repairsite', pid, 4, data)

    def _run(self):
        self.room = Game.rooms[self._data.room_name]
        self.controller = self.room.controller

        self.place_flag()
        self.run_creeps()

    def run_creep(self, creep):
        if creep.is_empty():
            creep.set_task('gather')
        elif creep.is_full() or creep.is_idle():
            creep.set_task('repair', {'site_id': self._data.site_id})

        creep.run_current_task()

    def is_completed(self):
        site = Game.getObjectById(self._data.site_id)

        if not site or site.hits == site.hitsMax:
            flag = Game.flags['RepairSite(' + str(self._data.room_name) + ')']
            if flag:
                flag.remove()
            return True

        return False

    def needs_creeps(self):
        return len(self._data.creep_names) < 1

    def is_valid_creep(self, creep):
        return creep.getActiveBodyparts(WORK) > 0 and creep.getActiveBodyparts(CARRY) > 0

    def gen_body(self, energy):
        body = [WORK, CARRY, MOVE]
        mod = [WORK, CARRY, MOVE]

        while self.get_body_cost(body.concat(mod)) <= energy:
            body = body.concat(mod)

        return body, None

    def place_flag(self):
        flags = self.room.flags

        site = Game.getObjectById(self._data.site_id)
        if not site:
            return

        x, y = site.pos.x, site.pos.y

        already_placed = False
        for flag in flags:
            if flag['name'] == 'RepairSite(' + str(self._data.room_name) + ')':
                if flag['pos']['x'] == x and flag['pos']['y'] == y:
                    already_placed = True
                    break
                else:
                    flag.remove()

        if not already_placed:
            self.room.createFlag(x, y, 'RepairSite(' + str(self._data.room_name) + ')', COLOR_RED)
