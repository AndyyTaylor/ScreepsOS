
import random
from defs import *  # noqa

from framework.process import Process

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class Spawning(Process):

    def __init__(self, pid, data={}):
        super().__init__('spawning', pid, 2, data)

    def _run(self):
        self.room = Game.rooms[self._data.room_name]
        if self.get_spawn_ticket():
            print(self.get_spawn_ticket()['data']['body'])
        for spawn in self.room.spawns:
            if not spawn.spawning:
                ticket = self.get_spawn_ticket()

                if ticket is not None:
                    name = str(random.randint(0, 10000))
                    result = spawn.spawnCreep(ticket['data']['body'], name)

                    if result == OK:
                        print('spawning', ticket['data']['body'])
                        ticket['completed'] = True
                        ticket['result']['name'] = name
                        Memory.creeps[name] = {'created': Game.time}

    def get_spawn_ticket(self):
        ticket = self.ticketer.get_highest_priority('spawn')
        return ticket
