
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

        self.run_creeps()

    def run_creep(self, creep):
        if creep.is_idle():
            sit_pos = __new__(RoomPosition(self._data.sit_x,
                                           self._data.sit_y, self._data.room_name))
            if creep.pos.inRangeTo(sit_pos, 0):
                tasks = [self.fill_up_cont, self.clear_cent_link, self.fill_terminal,
                         self.empty_creep]

                for task in tasks:
                    if task(creep):
                        break
            else:
                creep.set_task("travel", {"dest_x": self._data.sit_x, "dest_y": self._data.sit_y,
                                          "dest_room_name": self._data.room_name})

        creep.run_current_task()

    def fill_up_cont(self, creep):
        if self.room.storage.store[RESOURCE_ENERGY] < js_global.STORAGE_MIN[self.room.rcl]:
            return False

        center_link = Game.getObjectById(self._data.cent_link_id)
        up_link = Game.getObjectById(self._data.up_link_id)
        if _.isNull(center_link) or _.isNull(up_link):
            return False

        if center_link.cooldown != 0 or up_link.energy > 700:
            return False

        if center_link.energy >= up_link.energyCapacity - up_link.energy:
            center_link.transferEnergy(up_link)
        elif creep.is_empty():
            creep.withdraw(self.room.storage, RESOURCE_ENERGY)
        elif creep.carry[RESOURCE_ENERGY] > 0:
            creep.transfer(center_link, RESOURCE_ENERGY)
        else:
            creep.transfer(self.room.storage, Object.keys(creep.carry).pop())

        return True

    def clear_cent_link(self, creep):
        center_link = Game.getObjectById(self._data.cent_link_id)
        if _.isNull(center_link):
            return False
        name: str = 'hey'

        if center_link.energy == 0:
            return False

        if not creep.is_full():
            creep.withdraw(center_link, RESOURCE_ENERGY)
        else:
            creep.transfer(self.room.storage, Object.keys(creep.carry).pop())

        return True

    def fill_terminal(self, creep):
        terminal = self.room.terminal
        if _.isUndefined(terminal):
            return False

        reserves = self.room.storage.store[RESOURCE_ENERGY] < js_global.STORAGE_MIN[self.room.rcl]
        if terminal.store.energy < 30000 and not reserves:
            if creep.carry[RESOURCE_ENERGY] > 0:
                amt = min(creep.carry[RESOURCE_ENERGY], 30000 - terminal.store.energy)
                creep.transfer(terminal, RESOURCE_ENERGY, amt)
            else:
                creep.withdraw(self.room.storage, RESOURCE_ENERGY)

            return True

        storage = self.room.storage
        for rtype in Object.keys(storage.store):
            if storage.store[rtype] < 5000:
                continue

            if _.isUndefined(terminal.store[rtype]) or terminal.store[rtype] < 5000:
                if creep.carry[rtype] > 0:
                    if not _.isUndefined(terminal.store[rtype]):
                        amt = min(creep.carry[rtype], 5000 - terminal.store[rtype])
                    else:
                        amt = creep.carry[rtype]
                    amt = min(amt, storage.store[rtype] - 5000)
                    creep.transfer(terminal, rtype, amt)
                elif creep.is_full():
                    creep.transfer(storage, Object.keys(creep.carry).pop())
                else:
                    creep.withdraw(storage, rtype)

                return True

        return False

    def empty_creep(self, creep):
        if _.sum(creep.carry) == 0:
            return False

        creep.transfer(self.room.storage, Object.keys(creep.carry).pop())

        return True

    def needs_creeps(self):
        return len(self._data.creep_names) < 1

    def is_valid_creep(self, creep):
        return creep.memory.role == 'manager'

    def gen_body(self, energy):
        body = [CARRY, CARRY, MOVE]
        mod = [CARRY, CARRY, MOVE]
        carry_count = 2

        max_carry = 500
        while self.get_body_cost(body.concat(mod)) <= energy and carry_count < max_carry // 50:
            body = body.concat(mod)
            carry_count += 2

        return body, {'role': 'manager'}

    def init(self):
        base_flag = Game.flags[self._data.room_name]

        if not base_flag:
            return

        link_x = base_flag.pos.x + base['central_link']['x']
        link_y = base_flag.pos.y + base['central_link']['y']
        self._data.cent_link_id = self.load_link(link_x, link_y)

        pos = self.room.controller.pos
        structs = self.room.lookForAtArea(LOOK_STRUCTURES, pos.y - 1, pos.x - 1,
                                          pos.y + 1, pos.x + 1, True)
        for struct in structs:
            if struct.structure.structureType == STRUCTURE_LINK:
                self._data.up_link_id = struct.structure.id

                break

        self._data.sit_x = base_flag.pos.x + base['manager']['x']
        self._data.sit_y = base_flag.pos.y + base['manager']['y']

        self._data.has_init = True

    def load_link(self, link_x, link_y):
        structures = self.room.lookForAt(LOOK_STRUCTURES, link_x, link_y)
        for struct in structures:
            if struct.structureType == STRUCTURE_LINK:
                return struct.id

        return None
