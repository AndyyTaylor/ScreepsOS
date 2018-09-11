
from defs import *  # noqa

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')
__pragma__('noalias', 'name')


class RemoteWork(CreepProcess):

    def __init__(self, pid, data={}):
        super().__init__('remotework', pid, 4, data)

    def _run(self):
        self.room = Game.rooms[self._data.room_name]
        self.target_room = Game.rooms[self._data.target_room]

        self.run_creeps()

    def run_creep(self, creep):
        if creep.room.name != self._data.target_room:
            creep.moveTo(__new__(RoomPosition(25, 25, self._data.target_room)))
        else:
            if creep.is_empty() and creep.is_idle():
                if self.target_room.total_dropped_energy() > 100:
                    creep.set_task('gather')
                else:
                    sources = self.target_room.find(FIND_SOURCES_ACTIVE)
                    if len(sources) > 0:
                        creep.set_task('harvest', {'source_id': sources[0].id})
            elif creep.is_full() or creep.is_idle():
                sites = self.target_room.find(FIND_CONSTRUCTION_SITES)
                if len(sites) > 0:
                    creep.set_task('build', {'site_id': sites[0].id})
                else:
                    creep.set_task('upgrade')

        creep.run_current_task()

    def needs_creeps(self):
        return len(self._data.creep_names) < 1

    def is_valid_creep(self, creep):
        return creep.getActiveBodyparts(WORK) > 1 and creep.getActiveBodyparts(CARRY) > 0 and \
            not _.isUndefined(creep.memory.remote)

    def gen_body(self, energyAvailable):
        body = [WORK, CARRY, MOVE]
        mod = [WORK, CARRY, MOVE]
        total_work = 1

        while self.get_body_cost(body.concat(mod)) <= energyAvailable and total_work < 10:
            total_work += 1
            body = body.concat(mod)

        return body, {'remote': True}

    def is_completed(self):
        target_room = Game.rooms[self._data.target_room]
        if _.isUndefined(target_room):
            return False

        if target_room.rcl < 3 or len(target_room.spawns) == 0:
            return False

        return True
