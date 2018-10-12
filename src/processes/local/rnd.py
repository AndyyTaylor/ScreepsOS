
from defs import *  # noqa
from base import base

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class RND(CreepProcess):

    def __init__(self, pid, data=None):
        super().__init__('rnd', pid, 2, data)

        if self._pid != -1:
            self.room = Game.rooms[self._data.room_name]
            self.controller = self.room.controller

    def _run(self):
        if _.isUndefined(self._data.has_init):
            self.init()

        self.input1 = Game.getObjectById(self._data.input1_id)
        self.input2 = Game.getObjectById(self._data.input2_id)

        if _.isNull(self.input1) or _.isNull(self.input2):
            return

        self.room.visual.circle(self.input1.pos)
        self.room.visual.circle(self.input2.pos)

        self.run_creeps()

    def run_creep(self, creep):
        creep.moveTo(creep.room.controller)

    def needs_creeps(self):
        return len(self._data.creep_names) < 1

    def is_valid_creep(self, creep):
        return creep.memory.role == 'scientist'

    def gen_body(self, energy):
        body = [CARRY, CARRY, MOVE]
        mod = [CARRY, CARRY, MOVE]
        carry_count = 2

        max_carry = 500

        while self.get_body_cost(body.concat(mod)) <= energy and carry_count < max_carry // 50:
            body = body.concat(mod)
            carry_count += 2

        return body, {'role': 'scientist'}

    def init(self):
        base_flag = Game.flags[self._data.room_name]

        if not base_flag:
            return

        if self.room.rcl == 6:
            self._data.input1_id = self.load_lab_at(base_flag.pos.x + 8, base_flag.pos.y + 7).id
            self._data.input2_id = self.load_lab_at(base_flag.pos.x + 9, base_flag.pos.y + 7).id

        self._data.has_init = True

    def load_lab_at(self, x: int, y: int):
        for struct in self.room.lookForAt(LOOK_STRUCTURES, x, y):
            if struct.structureType == STRUCTURE_LAB:
                return struct

        return None

