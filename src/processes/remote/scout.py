
from defs import *  # noqa
from typing import Optional

from framework.creepprocess import CreepProcess
from processes.local.roomplanner import RoomPlanner

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')
__pragma__('noalias', 'name')


class Scout(CreepProcess):

    def __init__(self, pid, data=None):
        super().__init__('scout', pid, 4, data)

        if pid == -1:
            return

        self.room = Game.rooms[self._data.room_name]
        self.target_room = Game.rooms[self._data.target_room]

        if _.isUndefined(self._data.once_only):
            self._data.once_only = True

    def _run(self):
        self.run_creeps()

    def run_creep(self, creep):
        target_pos = __new__(RoomPosition(25, 25, self._data.target_room))
        creep.moveTo(target_pos, {'range': 24})

        if self.should_scout_room(creep.room):
            self.scout_room(creep.room)

    @staticmethod
    def should_scout_room(room: Room) -> bool:
        mem = Memory.rooms[room.name]
        if _.isUndefined(mem) or _.isUndefined(mem.last_updated) or mem.last_updated + js_global.SCOUT_FREQ < Game.time:
            return True

        return False

    def scout_room(self, room: Room):
        if _.isUndefined(Memory.rooms[room.name]):
            Memory.rooms[room.name] = {}

        mem = Memory.rooms[room.name]

        rp_process = RoomPlanner(-1, {'room_name': room.name})
        rp_process.room = room

        mem.scout_info = {
            'owner': self.get_room_owner(room),
            'claimable': self.get_room_owner(room) is None and not _.isUndefined(room.controller),
            'num_sources': len(room.sources),
            'fits_base': rp_process.place_base()
        }
        mem.last_updated = Game.time

        print(room.name, JSON.stringify(mem.scout_info))

    @staticmethod
    def get_room_owner(room: Room) -> Optional[str]:
        if _.isUndefined(room.controller):
            for struct in room.find(FIND_STRUCTURES):
                if struct.structureType == STRUCTURE_KEEPER_LAIR:
                    return js_global.INVADER_USERNAME

            return None  # Highway
        elif _.isUndefined(room.controller.owner):
            return None
        else:
            return room.controller.owner.username

    def needs_creeps(self):
        return len(self._data.creep_names) < 1

    def is_valid_creep(self, creep):
        return creep.memory.role == 'scout'

    def gen_body(self, energy):
        body = [MOVE]

        return body, {'role': 'scout'}

    def is_completed(self):
        if self._data.once_only and not _.isUndefined(self.target_room):
            return True

        return False
