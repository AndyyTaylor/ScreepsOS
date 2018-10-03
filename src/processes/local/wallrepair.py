
from defs import *  # noqa

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class WallRepair(CreepProcess):

    def __init__(self, pid, data={}):
        super().__init__('wallrepair', pid, 4, data)

        if pid != -1:
            self.room = Game.rooms[self._data.room_name]

    def _run(self):
        self.run_creeps()

    def run_creep(self, creep):
        site = Game.getObjectById(self._data.site_id)
        if not site or site.hits >= self.room.memory.walls.hits:
            self._data.site_id = self.select_site()
            site = Game.getObjectById(self._data.site_id)
            creep.clear_task()

        if self._data.site_id is None:
            return

        if creep.is_empty():
            if not _.isUndefined(self.room.storage) and \
                    self.room.storage.store[RESOURCE_ENERGY] > js_global.STORAGE_MIN[self.room.rcl]:
                creep.set_task('withdraw', {'target_id': self.room.storage.id,
                                            'type': RESOURCE_ENERGY})
            else:
                creep.set_task('gather')
        elif creep.is_full() or creep.is_idle():
            creep.set_task('repair', {'site_id': site.id})

        creep.run_current_task()

    def select_site(self):
        min_wall = None
        for wall in self.room.damaged_walls:
            if min_wall is None or wall.hits < min_wall.hits:
                min_wall = wall

        if min_wall is not None:
            return min_wall.id

        return None

    def is_completed(self):
        return len(self.room.damaged_walls) == 0 and self._data.site_id is None

    def needs_creeps(self):
        return len(self._data.creep_names) < 1

    def is_valid_creep(self, creep):
        return creep.memory.role == 'wallrepairer'

    def gen_body(self, energy):
        body = [WORK, CARRY, MOVE]
        mod = [WORK, CARRY, MOVE]
        total_work = 1

        while self.get_body_cost(body.concat(mod)) <= energy and total_work < 6:
            body = body.concat(mod)
            total_work += 1

        return body, {'role': 'wallrepairer'}
