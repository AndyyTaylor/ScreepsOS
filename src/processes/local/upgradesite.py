
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
            link = Game.getObjectById(self._data.link_id)
            if not _.isNull(link) and link.energy > 0:
                creep.set_task('withdraw', {'target_id': self._data.link_id})
            elif not _.isUndefined(self.room.storage) and \
                    self.room.storage.store[RESOURCE_ENERGY] > js_global.STORAGE_MIN[self.room.rcl]:
                creep.set_task('withdraw', {'target_id': self.room.storage.id})
            else:
                creep.set_task('gather')
        elif creep.is_full() or creep.is_idle():
            creep.set_task('upgrade')

        creep.run_current_task()

    def needs_creeps(self):
        if len(self.room.construction_sites):
            return len(self._data.creep_names) < 1  # Scale this
        else:
            return len(self._data.creep_names) < 1 + self.room.get_additional_workers()

    def is_valid_creep(self, creep):
        return creep.getActiveBodyparts(WORK) > 0 and creep.getActiveBodyparts(CARRY) > 0

    def gen_body(self, energy):
        body = [WORK, CARRY, MOVE]
        mod = [WORK, CARRY, MOVE]
        count = 1

        while self.get_body_cost(body.concat(mod)) <= energy and count < 10:
            body = body.concat(mod)
            count += 1

        return body, None

    def init(self):  # This should request certain buildings. container / link etc
        if self.room.rcl >= 5:
            self.load_link()

        self._data.has_init = True

    def load_link(self):
        link_id = None
        pos = self.room.controller.pos
        x, y = pos.x, pos.y
        nearby_structs = self.room.lookForAtArea(LOOK_STRUCTURES, y - 1, x - 1, y + 1, x + 1, True)
        for struct in nearby_structs:
            if struct.structure.structureType == STRUCTURE_LINK:
                link_id = struct.structure.id

        if link_id is None:
            nearby_terrain = self.room.lookForAtArea(LOOK_TERRAIN, y - 1, x - 1, y + 1, x + 1, True)
            for terrain in nearby_terrain:
                if terrain.terrain != 'wall':
                    tid = self.ticketer.add_ticket('build', self._pid, {'type': STRUCTURE_LINK,
                                                                        'x': terrain.x,
                                                                        'y': terrain.y})
                    self._data.build_tickets.append(tid)

                    return
        else:
            self._data.link_id = link_id

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
