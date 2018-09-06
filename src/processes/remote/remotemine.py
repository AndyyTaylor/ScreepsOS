
from defs import *  # noqa

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')
__pragma__('noalias', 'name')


class RemoteMine(CreepProcess):

    def __init__(self, pid, data={}):
        super().__init__('remotemine', pid, 4, data)

    def _run(self):
        self.room = Game.rooms[self._data.room_name]
        self.mine_room = Game.rooms[self._data.mine_room]

        if _.isUndefined(self._data.has_init):
            self.init()

        self.run_creeps()

    def run_creep(self, creep):
        if not _.isUndefined(self.mine_room):
            Memory.rooms[self._data.mine_room].last_updated = Game.time

            ticks_left = self.mine_room.controller.reservation.ticksToEnd
            Memory.rooms[self._data.mine_room].reservation = ticks_left

        if creep.room.name != self._data.mine_room:
            creep.moveTo(__new__(RoomPosition(25, 25, self._data.mine_room)))
        elif creep.getActiveBodyparts(CLAIM) > 0:
            if creep.pos.isNearTo(self.mine_room.controller):
                creep.reserveController(self.mine_room.controller)
            else:
                creep.moveTo(creep.room.controller)
        else:
            source = Game.getObjectById(creep.memory.source_id)
            if creep.pos.isNearTo(source):
                creep.harvest(source)
            else:
                creep.moveTo(source)

        creep.run_current_task()

    def needs_creeps(self):
        if not self._data.has_init:
            return not self.has_reserver()

        return len(self._data.creep_names) - 1 < self._data.num_sources or self.needs_reserver()

    def has_reserver(self):
        for name in self._data.creep_names:
            creep = Game.creeps[name]
            if creep.getActiveBodyparts(CLAIM) > 0:
                return True

        return False

    def needs_reserver(self):
        return not self.has_reserver()  # Something to do with the timer on the controller

    def is_valid_creep(self, creep):
        valid = False
        if not self.has_reserver() and creep.getActiveBodyparts(CLAIM) > 0:
            valid = True

        if len(self._data.creep_names) - 1 < self._data.num_sources and \
                creep.getActiveBodyparts(WORK) > 0 and creep.getActiveBodyparts(CARRY) < 3 and \
                not _.isUndefined(creep.memory.source_id):
            valid = True

        return valid

    def gen_body(self, energyAvailable):
        if self.needs_reserver():
            body, memory = self.gen_reserver(energyAvailable)
        else:
            body, memory = self.gen_miner(energyAvailable)

        return body, memory

    def gen_reserver(self, energyAvailable):
        body = [CLAIM, MOVE, CLAIM, MOVE]
        mod = [CLAIM, MOVE]
        total_claim = 2

        while self.get_body_cost(body.concat(mod)) <= energyAvailable and total_claim < 4:
            total_claim += 1
            body = body.concat(mod)

        return body, None

    def gen_miner(self, energyAvailable):
        body = [WORK, MOVE]
        mod = [WORK, MOVE]
        total_work = 1

        while self.get_body_cost(body.concat(mod)) <= energyAvailable and total_work < 6:
            total_work += 1
            body = body.concat(mod)

        memory = {}
        taken_sources = []
        for name in self._data.creep_names:
            creep = Game.creeps[name]
            if not _.isUndefined(creep.memory.source_id):
                taken_sources.append(creep.memory.source_id)

        for id in self._data.source_ids:
            if not taken_sources.includes(id):
                memory.source_id = id

        return body, memory

    def init(self):
        mine_room = Game.rooms[self._data.mine_room]
        if _.isUndefined(mine_room):
            return

        self._data.num_sources = len(mine_room.find(FIND_SOURCES))
        self._data.source_ids = [source.id for source in mine_room.find(FIND_SOURCES)]

        self._data.has_init = True
