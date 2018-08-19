
import random
from defs import *  # noqa

from framework.process import Process

__pragma__('noalias', 'keys')


class CreepProcess(Process):

    def __init__(self, name, pid, priority, data={}):
        super().__init__(name, pid, priority, data)

        if _.isUndefined(self._data.creep_names):
            self._data.creep_names = []

    def run(self):
        if self.needs_creeps():
            self.assign_creeps()

        super().run()

    def assign_creeps(self):
        for name in Object.keys(Game.creeps):
            creep = Game.creeps[name]

            if not creep.assigned:
                self.assign_creep(creep)

            if not self.needs_creeps():
                return

        Game.spawns['Spawn1'].spawnCreep([WORK, CARRY, MOVE], random.randint(0, 10000))

    def assign_creep(self, creep):
        creep.assign(self._pid)

        self._data.creep_names.append(creep['name'])

    def needs_creeps(self):
        return False

    def value_creep(self, creep):
        return 0
