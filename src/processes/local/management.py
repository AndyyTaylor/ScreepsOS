
from defs import *  # noqa
from base import base

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class Management(CreepProcess):

    def __init__(self, pid, data={}):
        super().__init__('management', pid, 2, data)

        if self._pid != -1:
            self.room = Game.rooms[self._data.room_name]
            self.controller = self.room.controller

    def _run(self):
        if _.isUndefined(self._data.has_init):
            self.init()

        self.place_flag()

        self.run_creeps()

    def run_creep(self, creep):
        if creep.is_idle():
            sit_pos = __new__(RoomPosition(self._data.sit_x,
                                           self._data.sit_y, self._data.room_name))
            if creep.pos.inRangeTo(sit_pos, 0):
                center_link = Game.getObjectById(self._data.cent_link_id)
                up_link = Game.getObjectById(self._data.up_link_id)
                if self.room.storage.store[RESOURCE_ENERGY] > js_global.STORAGE_MIN[self.room.rcl]:
                    if creep.is_empty():
                        creep.withdraw(room.storage, RESOURCE_ENERGY)
                    elif center_link.energy < center_link.energyCapacity and \
                            up_link.energy < up_link.energyCapacity:
                        creep.transfer(center_link, RESOURCE_ENERGY)
                        center_link.transferEnergy(up_link)
            else:
                creep.set_task("travel", {"dest_x": self._data.sit_x, "dest_y": self._data.sit_y})

        creep.run_current_task()

    def needs_creeps(self):
        return len(self._data.creep_names) < 1

    def is_valid_creep(self, creep):
        return creep.getActiveBodyparts(CARRY) > 0 and creep.getActiveBodyparts(WORK) < 1 and \
            _.isUndefined(creep.memory.haul_ind)

    def gen_body(self, energy):
        body = [CARRY, MOVE]
        mod = [CARRY, MOVE]
        carry_count = 1

        max_carry = 300
        while self.get_body_cost(body.concat(mod)) <= energy and carry_count < max_carry // 50:
            body = body.concat(mod)
            carry_count += 1

        return body, None

    def init(self):
        base_flag = Game.flags[self._data.room_name]

        if not base_flag:
            return

        link_x = base_flag.pos.x + base['central_link']['x']
        link_y = base_flag.pos.x + base['central_link']['y']
        self._data.cent_link_id = self.load_link(link_x, link_y)

        self._data.sit_x = base_flag.pos.x + base['manager']['x']
        self._data.sit_y = base_flag.pos.y + base['manager']['y']

        self._data.has_init = True

    def load_link(self, link_x, link_y):
        structures = self.room.lookForAt(LOOK_STRUCTURES, link_x, link_y)
        for struct in structures:
            if struct.structureType == STRUCTURE_LINK:
                return struct.id

        return None

    def place_flag(self):
        flags = self.room.flags

        x, y = self._data.hold_x, self._data.hold_y

        already_placed = False
        for flag in flags:
            if flag['name'] == 'Manager(' + str(self._data.room_name) + ')':
                already_placed = True
                break

        if not already_placed:
            self.room.createFlag(x, y, 'Manager(' + str(self._data.room_name) + ')', 'black')