
from defs import *  # noqa

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')
__pragma__('noalias', 'name')


class Claim(CreepProcess):

    def __init__(self, pid, data=None):
        super().__init__('claim', pid, 4, data)

    def _run(self):
        self.room: Room = Game.rooms[self._data.room_name]
        self.target_room: Room = Game.rooms[self._data.target_room]

        print('claiming', self._data.room_name, len(self._data.creep_names))

        self.run_creeps()

    def run_creep(self, creep):
        if creep.room.name != self._data.target_room:
            creep.moveTo(__new__(RoomPosition(25, 25, self._data.target_room)))
        elif creep.pos.isNearTo(self.target_room.controller):
            if self.target_room.is_city():
                for struct in self.target_room.find(FIND_STRUCTURES):
                    struct.destroy()

                self.kill()
            else:
                creep.claimController(self.target_room.controller)
        else:
            creep.moveTo(creep.room.controller)

        creep.run_current_task()

    def needs_creeps(self):
        return len(self._data.creep_names) < 1

    def is_valid_creep(self, creep):
        return creep.getActiveBodyparts(CLAIM) > 0

    def gen_body(self, energyAvailable):
        body = [CLAIM, MOVE]

        return body, None

    def is_completed(self):
        target_room = Game.rooms[self._data.target_room]
        if not _.isUndefined(target_room) and target_room.is_city():
            return True

        return False
