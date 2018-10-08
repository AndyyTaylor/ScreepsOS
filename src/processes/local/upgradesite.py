
from defs import *  # noqa

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class UpgradeSite(CreepProcess):

    def __init__(self, pid, data={}):
        super().__init__('upgradesite', pid, 3, data)

        if pid != -1:
            self.room = Game.rooms[self._data.room_name]
            self.controller = self.room.controller

    def _run(self):
        if _.isUndefined(self._data.has_init):
            self.init()

        self.run_creeps()

    def run_creep(self, creep):
        if creep.room != self.room:
            creep.moveTo(self.room.controller)
        else:
            if creep.carry.energy < creep.carryCapacity / 2:
                link = Game.getObjectById(self._data.link_id)
                if not _.isNull(link) and link.energy > 0:
                    creep.set_task('withdraw', {'target_id': self._data.link_id})
                elif not _.isUndefined(self.room.storage) and \
                        self.room.storage.store[RESOURCE_ENERGY] > \
                        js_global.STORAGE_MIN[self.room.rcl] and \
                        creep.is_empty():
                    creep.set_task('withdraw', {'target_id': self.room.storage.id,
                                                'type': RESOURCE_ENERGY})
                elif creep.is_empty():
                    creep.set_task('gather')

                creep.run_current_task()

            if not creep.is_empty():
                creep.set_task('upgrade')

            sign = self.room.controller.sign
            if (_.isUndefined(sign) or sign.text != js_global.CONTROLLER_SIGN) and _.isUndefined(self._data.no_sign):
                res = creep.moveTo(self.room.controller)
                if res == ERR_NO_PATH or creep.ticksToLive < 1400:
                    self._data.no_sign = True
                else:
                    creep.set_task('sign')

            creep.run_current_task()

    def needs_creeps(self):
        if len(self.room.construction_sites) > 0:
            return len(self._data.creep_names) < 1  # Scale this
        else:
            return len(self._data.creep_names) < 1 + self.room.get_additional_workers()

    def is_valid_creep(self, creep):
        return creep.memory.role == 'upgrader'

    def gen_body(self, energy):
        body = [WORK, CARRY, MOVE]
        count = 1

        if self.room.rcl < 5:
            mod = [WORK, CARRY, MOVE]
            add_mod = 1
        else:
            mod = [WORK, WORK, MOVE]
            add_mod = 2

        while self.get_body_cost(body.concat(mod)) <= energy and count < 11:
            body = body.concat(mod)
            count += add_mod

        return body, {'role': 'upgrader'}

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
                                                                        'y': terrain.y,
                                                                        'city': self._data.room_name
                                                                        })
                    self._data.build_tickets.append(tid)

                    return
        else:
            self._data.link_id = link_id
