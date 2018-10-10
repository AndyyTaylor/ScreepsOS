
from defs import *  # noqa

from framework.process import Process

__pragma__('noalias', 'keys')
__pragma__('noalias', 'name')


class CreepProcess(Process):

    def __init__(self, name, pid, priority, data=None):
        super().__init__(name, pid, priority, data)

        if _.isUndefined(self._data.creep_names):
            self._data.creep_names = []

        if _.isUndefined(self._data.spawn_tickets):
            self._data.spawn_tickets = []

        if pid != -1:
            self.room = Game.rooms[self._data.room_name]

    def run(self):
        if self.needs_creeps():
            self.assign_creeps()

        super().run()

    def _run(self):
        self.run_creeps()

    def run_creeps(self):
        expired_creeps = []
        for name in self._data.creep_names:
            creep = Game.creeps[name]

            if not creep:
                cmemory = Memory.creeps[name]
                if (_.isUndefined(cmemory) or _.isUndefined(cmemory['created']) or
                        cmemory['created'] < Game.time - cmemory['spawnTime'] - 5):

                    expired_creeps.append(name)

                continue

            self.keep_creep_safe(creep)

            if _.isUndefined(creep.memory.keep_safe):
                self.run_creep(creep)

        for name in expired_creeps:
            self._data.creep_names.remove(name)

    def keep_creep_safe(self, creep: Creep) -> None:
        self.check_creep_danger(creep)

        if not _.isUndefined(creep.memory.keep_safe) and _.isUndefined(self._data.military):
            self.move_creep_to_safety(creep)

    def check_creep_danger(self, creep: Creep) -> None:
        if not _.isUndefined(creep.room.memory) and not _.isUndefined(creep.room.memory.threats) and \
                creep.room.memory.threats.safe_tick > Game.time and not self._data.military:
            creep.memory.keep_safe = creep.room.name

    def move_creep_to_safety(self, creep: Creep):
        room_mem = Memory.rooms[creep.memory.keep_safe]
        if not _.isUndefined(room_mem.threats.safe_tick) and room_mem.threats.safe_tick > Game.time:
            # Has to be nested for else to eval properly
            if creep.pos.x > 47 or creep.pos.x < 3 or creep.pos.y > 47 or creep.pos.y < 3 or \
                    (not _.isUndefined(creep.room.memory) and not _.isUndefined(creep.room.memory.threats) and
                     creep.room.memory.threats.safe_tick > Game.time):
                creep.moveTo(self.room.controller)
        else:
            del creep.memory.keep_safe

    def assign_creeps(self):
        self.assign_from_tickets()

        if not self.needs_creeps():
            return

        self.assign_from_existing()

        if not self.needs_creeps():
            return

        self.create_spawn_ticket()

    def assign_from_tickets(self):
        if len(self._data.spawn_tickets) > 0:
            ticket = self.ticketer.get_ticket(self._data.spawn_tickets[0])

            if not ticket:
                self._data.spawn_tickets.splice(0, 1)
            elif ticket['completed']:
                if not _.isUndefined(Memory.creeps[ticket['result']['name']]):
                    Memory.creeps[ticket['result']['name']].assigned = self._pid
                    self._data.creep_names.append(ticket['result']['name'])
                    self.ticketer.delete_ticket(self._data.spawn_tickets[0])
                else:
                    print("Wtf")
                self._data.spawn_tickets.splice(0, 1)

    def assign_from_existing(self) -> None:
        for name in self.room.creeps:
            creep = Game.creeps[name]

            if not creep.assigned and creep.memory.created < Game.time - 10 and \
                    self.is_valid_creep(creep):

                self.assign_creep(creep)

            if not self.needs_creeps():
                return

    def create_spawn_ticket(self) -> None:
        if len(self._data.spawn_tickets) < 1:
            room = Game.rooms[self._data.room_name]
            body, memory = self.gen_body(room.get_spawn_energy())

            if memory is None:
                memory = {}

            ticket = {
                'body': body,
                'memory': memory,
                'city': self._data.room_name
            }
            tid = self.ticketer.add_ticket('spawn', self._pid, ticket)
            self._data.spawn_tickets.append(tid)

    def assign_creep(self, creep: Creep):
        creep.assign(self._pid)

        self._data.creep_names.append(creep.name)

    def get_body_cost(self, body):
        total = 0
        for part in body:
            total += BODYPART_COST[part]

        return total

    def gen_body(self, energy):
        return self._gen_body(energy, self.filter_creep_names())

    def _gen_body(self, energy, creep_names):
        return [WORK, CARRY, MOVE]

    def is_valid_creep(self, creep):
        return True

    def needs_creeps(self):
        return self._needs_creeps(self.filter_creep_names())

    def filter_creep_names(self):
        new_names = []
        for name in self._data.creep_names:
            creep = Game.creeps[name]
            if not creep:
                continue

            if creep.ticksToLive < len(creep.body) * CREEP_SPAWN_TIME:
                # print("Not including", name)
                pass
            else:
                new_names.append(name)

        return new_names

    def run_creep(self, creep):
        return

    def _needs_creeps(self, names):
        return False
