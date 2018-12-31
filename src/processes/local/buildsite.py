
from defs import *  # noqa

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class BuildSite(CreepProcess):

    def __init__(self, pid, data=None):
        super().__init__('buildsite', pid, 5, data)

        if pid != -1:
            self.room = Game.rooms[self._data.room_name]
            self.controller = self.room.controller

    def _run(self):
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
            creep.set_task('build', {'site_id': self._data.site_id})

        creep.run_current_task()

    def is_completed(self):
        site = Game.getObjectById(self._data.site_id)

        if not site or _.isUndefined(site.progress) or not \
                Object.keys(Game.constructionSites).includes(self._data.site_id):

            return True

        return False

    def needs_creeps(self):
        return len(self._data.creep_names) < 1 + self.room.get_additional_workers()  # Scale this

    def is_valid_creep(self, creep):
        return creep.memory.role == 'worker'

    def gen_body(self, energy):
        body = [WORK, CARRY, MOVE]
        mod = [WORK, CARRY, MOVE]
        count = 1

        while self.get_body_cost(body.concat(mod)) <= energy and count < 5:
            body = body.concat(mod)
            count += 1

        return body, {'role': 'worker'}
