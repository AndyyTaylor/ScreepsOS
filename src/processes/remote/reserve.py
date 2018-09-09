
from defs import *  # noqa

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')
__pragma__('noalias', 'name')


class Reserve(CreepProcess):

    def __init__(self, pid, data={}):
        super().__init__('reserve', pid, 4, data)

    def _run(self):
        self.room = Game.rooms[self._data.room_name]
        self.target_room = Game.rooms[self._data.target_room]

        if not _.isUndefined(self.target_room):
            if _.isUndefined(Memory.rooms[self._data.target_room]):
                Memory.rooms[self._data.target_room] = {}

            Memory.rooms[self._data.target_room].last_updated = Game.time

            if not _.isUndefined(self.target_room.controller.reservation):
                ticks_left = self.target_room.controller.reservation.ticksToEnd
            else:
                ticks_left = 0
            Memory.rooms[self._data.target_room].reservation = ticks_left

            if _.isUndefined(Memory.rooms[self._data.target_room].num_sources):
                source_ids = [source.id for source in self.target_room.find(FIND_SOURCES)]
                Memory.rooms[self._data.target_room].num_sources = len(source_ids)
                Memory.rooms[self._data.target_room].sources = source_ids

        self.run_creeps()

    def run_creep(self, creep):
        if creep.room.name != self._data.target_room:
            creep.moveTo(__new__(RoomPosition(25, 25, self._data.target_room)))
        elif creep.pos.isNearTo(self.target_room.controller):
            creep.reserveController(self.target_room.controller)
        else:
            creep.moveTo(creep.room.controller)

        creep.run_current_task()

    def needs_creeps(self):
        if _.isUndefined(Memory.rooms[self._data.target_room]) or \
                _.isUndefined(Memory.rooms[self._data.target_room].reservation):
            return len(self._data.creep_names) < 1

        last_update = Memory.rooms[self._data.target_room].last_updated
        last_ticks = Memory.rooms[self._data.target_room].reservation
        ticks_left = last_ticks - (Game.time - last_update)

        if ticks_left < js_global.MIN_RESERVE_TICKS:
            return len(self._data.creep_names) < 1

        return False

    def is_valid_creep(self, creep):
        return creep.getActiveBodyparts(CLAIM) > 1

    def gen_body(self, energyAvailable):
        body = [CLAIM, MOVE, CLAIM, MOVE]
        mod = [CLAIM, MOVE]
        total_claim = 2

        while self.get_body_cost(body.concat(mod)) <= energyAvailable and total_claim < 4:
            total_claim += 1
            body = body.concat(mod)

        return body, None
