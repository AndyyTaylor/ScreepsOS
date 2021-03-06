
import random
from defs import *  # noqa

from framework.process import Process

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class Spawning(Process):

    def __init__(self, pid, data={}):
        super().__init__('spawning', pid, 0, data)

    def _run(self):
        self.room = Game.rooms[self._data.room_name]

        # ticket = self.get_spawn_ticket()
        # if ticket is not None:
        #     body = ticket['data']['body']
        #     body.sort()
        #     print('soon spawning', body)
        # else:
        #     print('no spawn tickets')

        for spawn in self.room.spawns:
            if not spawn.spawning:
                ticket = self.get_spawn_ticket()

                if ticket is not None:
                    name = str(random.randint(0, 10000))
                    body = ticket['data']['body']
                    body.sort(lambda p: js_global.BODY_ORDER.indexOf(p))
                    if body.includes(HEAL):
                        body.remove(HEAL)
                        body.append(HEAL)
                    result = spawn.spawnCreep(body, name)

                    if result == OK:
                        # print('spawning', body)
                        ticket['completed'] = True
                        ticket['result']['name'] = name
                        Memory.creeps[name] = {'created': Game.time, 'city': self._data.room_name,
                                               'spawnTime': len(body) * 3 + 10}  # Safe buffer of 10
                        if ticket['data']['memory']:
                            Memory.creeps[name] = Object.assign(Memory.creeps[name],
                                                                ticket['data']['memory'])
                    elif result == ERR_NOT_ENOUGH_ENERGY and \
                            self.room.energyAvailable >= self.room.get_spawn_energy():

                        self.ticketer.delete_ticket(ticket['tid'])

    def get_spawn_ticket(self):
        ticket = self.ticketer.get_highest_priority('spawn', self._data.room_name)
        return ticket
