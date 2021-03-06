
from defs import *  # noqa

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class RepairSite(CreepProcess):

    def __init__(self, pid, data={}):
        super().__init__('repairsite', pid, 3, data)

    def _run(self):
        self.room = Game.rooms[self._data.room_name]
        self.controller = self.room.controller

        self.run_creeps()

    def run_creep(self, creep):
        if creep.is_empty():
            if not _.isUndefined(self.room.storage) and \
                    self.room.storage.store[RESOURCE_ENERGY] > js_global.STORAGE_MIN[self.room.rcl]:
                creep.set_task('withdraw', {'target_id': self.room.storage.id,
                                            'type': RESOURCE_ENERGY})
            else:
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
        return creep.memory.role == 'worker'

    def gen_body(self, energy):
        body = [WORK, CARRY, MOVE]
        mod = [WORK, CARRY, MOVE]
        total_work = 1

        while self.get_body_cost(body.concat(mod)) <= energy and total_work < 5:
            body = body.concat(mod)
            total_work += 1

        return body, {'role': 'worker'}
