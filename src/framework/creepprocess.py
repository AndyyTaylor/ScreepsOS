
from defs import *  # noqa

from framework.process import Process

__pragma__('noalias', 'keys')
__pragma__('noalias', 'name')


class CreepProcess(Process):

    def __init__(self, name, pid, priority, data={}):
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

    def run_creeps(self):
        expired_creeps = []
        for name in self._data.creep_names:
            creep = Game.creeps[name]

            if not creep:
                cmemory = Memory.creeps[name]
                if (_.isUndefined(cmemory) or
                        _.isUndefined(cmemory['created']) or
                        cmemory['created'] < Game.time - cmemory['spawnTime']):

                    expired_creeps.append(name)

                continue

            if not _.isUndefined(creep.room.memory) and not \
                    _.isUndefined(creep.room.memory.threats):
                if creep.room.memory.threats.safe_tick > Game.time and not self._data.military:
                    creep.moveTo(self.room.controller)
                    creep.memory.keep_safe = Game.time + 100
                else:
                    self.run_creep(creep)
            elif not _.isUndefined(creep.memory.keep_safe) and creep.memory.keep_safe > Game.time \
                    and _.isUndefined(self._data.military):
                if creep.pos.x > 47 or creep.pos.x < 3 or creep.pos.y > 47 or creep.pos.y < 3:
                    creep.moveTo(self.room.controller)
            else:
                self.run_creep(creep)

        for name in expired_creeps:
            self._data.creep_names.remove(name)

    def assign_creeps(self):
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

        if not self.needs_creeps():
            return

        for name in self.room.creeps:
            creep = Game.creeps[name]

            # if creep.memory.early:
            #     creep.say("Early")

            if not creep.assigned and creep.memory.created < Game.time - 10 and \
                    self.is_valid_creep(creep):

                self.assign_creep(creep)

            if not self.needs_creeps():
                return

        if len(self._data.spawn_tickets) < 1:
            room = Game.rooms[self._data.room_name]
            body, memory = self.gen_body(room.get_spawn_energy())
            if memory is None:
                memory = {}

            tid = self.ticketer.add_ticket('spawn', self._pid,
                                           {'body': body, 'memory': memory,
                                            'city': self._data.room_name})
            self._data.spawn_tickets.append(tid)

        # Game.spawns['Spawn1'].spawnCreep([WORK, CARRY, MOVE], random.randint(0, 10000))

    def assign_creep(self, creep):
        creep.assign(self._pid)

        self._data.creep_names.append(creep['name'])

    def get_body_cost(self, body):
        total = 0
        for part in body:
            total += BODYPART_COST[part]

        return total

    def gen_body(self, energyAvailable):
        return [WORK, CARRY, MOVE]

    def is_valid_creep(self, creep):
        return True

    def needs_creeps(self):
        return False

    def value_creep(self, creep):
        return 0

    def run_creep(self, creep):
        return
