
from defs import *  # noqa
from base import base

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')
__pragma__('noalias', 'name')


class FeedSite(CreepProcess):

    def __init__(self, pid, data=None):
        super().__init__('feedsite', pid, 1, data)

        if self._pid != -1:
            self.room = Game.rooms[self._data.room_name]
            self.controller = self.room.controller

    def _run(self):
        if _.isUndefined(self._data.has_init):
            self.init()

        # if not _.isUndefined(self._data.withdraw_id):
        #     self.room.visual.circle(self._data.hold_x, self._data.hold_y,
        #                             {'fill': 'green', 'radius': 0.4})

        # if not _.isUndefined(self._data.positions):
        #     for i, pos in enumerate(self._data.positions[:-1]):
        #         self.room.visual.line(pos, self._data.positions[i + 1])

        self.run_creeps()

    def run_creep(self, creep):
        # creep.say("Feeder")
        cont = Game.getObjectById(self._data.withdraw_id)

        storage = creep.room.storage
        flag = False
        if not _.isUndefined(storage):
            if creep.memory.task_name == 'gather' and storage.store[RESOURCE_ENERGY] > 0:
                flag = True

        if creep.is_idle() or flag:
            if creep.is_empty():
                if not creep.room.is_full() and not _.isNull(cont) and \
                        cont.store[RESOURCE_ENERGY] > 0:
                    creep.set_task('withdraw', {'target_id': self._data.withdraw_id,
                                                'type': RESOURCE_ENERGY})
                elif not _.isUndefined(storage) and storage.store[RESOURCE_ENERGY] > 0:
                    creep.set_task('withdraw', {'target_id': storage.id, 'type': RESOURCE_ENERGY})
                elif _.isUndefined(creep.room.storage) or storage.store[RESOURCE_ENERGY] == 0:
                    creep.set_task('gather')
            elif not creep.room.is_full() and not creep.is_empty():
                creep.set_task('feed')
            elif not _.isNull(cont) and _.sum(cont.store) < cont.storeCapacity:
                creep.set_task('deposit', {'target_id': self._data.withdraw_id})

            if creep.is_idle():
                creep.set_task('travel', {'dest_x': self._data.hold_x,
                                          'dest_y': self._data.hold_y,
                                          'dest_room_name': self._data.room_name})

        creep.run_current_task()

    def needs_creeps(self):
        return len(self._data.creep_names) < 1

    def is_valid_creep(self, creep):
        return creep.memory.role == 'feeder'

    def gen_body(self, energy):
        if self.room.rcl > 4:
            body = [CARRY, CARRY, MOVE]
            mod = [CARRY, CARRY, MOVE]
            carry_mod = 2
            carry_count = 2
        else:
            body = [CARRY, MOVE]
            mod = [CARRY, MOVE]
            carry_mod = 1
            carry_count = 1

        if self.room.rcl < 5:
            max_carry = 300
        elif self.room.rcl < 7:
            max_carry = 450
        else:
            max_carry = 600

        while self.get_body_cost(body.concat(mod)) <= energy and carry_count < max_carry // 50:
            body = body.concat(mod)
            carry_count += carry_mod

        return body, {'role': 'feeder'}

    def init(self):
        base_flag = Game.flags[self._data.room_name]
        feed_path = base['feedpaths'][self._data.index]

        if not base_flag:
            return

        self._data.hold_x = base_flag.pos.x + feed_path['hold_x']
        self._data.hold_y = base_flag.pos.y + feed_path['hold_y']

        structures = self.room.lookForAt(LOOK_STRUCTURES, self._data.hold_x, self._data.hold_y)
        for structure in structures:
            if structure.structureType == STRUCTURE_CONTAINER:
                self._data.withdraw_id = structure.id

        landmarks = base['feedpaths'][self._data.index]['landmarks']
        if not _.isUndefined(landmarks):
            start = {"x": self._data.hold_x,
                     "y": self._data.hold_y, "roomName": self._data.room_name}
            positions = [start]

            for pos in landmarks:
                pos = __new__(RoomPosition(pos['x'] + base_flag.pos.x,
                                           pos['y'] + base_flag.pos.y,
                                           self._data.room_name))
                goal = {"pos": pos, "range": 0}

                result = PathFinder.search(start, goal,
                                           {'roomCallback': lambda r:
                                            self.room.basic_matrix(True)})

                for position in result.path:
                    positions.append(position)

                start = goal.pos

            self._data.positions = positions

        self._data.has_init = True
