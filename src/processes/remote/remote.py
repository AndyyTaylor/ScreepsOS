
from defs import *  # noqa
from typing import List

from framework.process import Process

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class Remote(Process):

    def __init__(self, pid: int, data=None) -> None:
        super().__init__('remote', pid, 3, data)

    def _run(self) -> None:
        self.room: Room = Game.rooms[self._data.room_name]

        to_scout: List[str] = self.room.memory.to_scout
        self.launch_scouts(to_scout)

        if self.room.rcl >= 3:
            to_claim: List[str] = self.room.memory.to_claim
            self.launch_claims(to_claim)

            to_work: List[str] = self.room.memory.to_work
            self.launch_remote_work(to_work)

        if self.room.rcl >= 4 and not _.isUndefined(self.room.storage):
            should_mine: List[str] = self.room.memory.remotes
            self.launch_reserves(should_mine)
            self.launch_mines(should_mine)
            self.launch_hauls(should_mine)

    def launch_reserves(self, should_reserve: List[str]) -> None:
        if self.scheduler.count_by_name('reserve', self._pid) < len(should_reserve):
            is_reserving = []

            for proc in self.scheduler.proc_by_name('reserve', self._pid):
                is_reserving.append(proc['data'].target_room)

            for reserve_room in should_reserve:
                if not is_reserving.includes(reserve_room):
                    self.launch_child_process('reserve', {'room_name': self._data.room_name,
                                                          'target_room': reserve_room})

    def launch_mines(self, should_mine: List[str]) -> None:
        rmines = self.scheduler.proc_by_name('remotemine', self._pid)
        for room in should_mine:
            if _.isUndefined(Memory.rooms[room]) or _.isUndefined(Memory.rooms[room].num_sources):
                continue

            room_mines = _.filter(rmines, lambda m: m['data'].mine_room == room)
            if len(room_mines) < Memory.rooms[room].num_sources:
                taken = [m['data'].source_id for m in room_mines]

                for sid in Memory.rooms[room].sources:
                    if not taken.includes(sid):
                        self.launch_child_process('remotemine', {'room_name': self._data.room_name,
                                                                 'mine_room': room,
                                                                 'source_id': sid})

    def launch_hauls(self, should_haul: List[str]) -> None:
        rhauls = self.scheduler.proc_by_name('remotehaul', self._pid)
        for room in should_haul:
            if _.isUndefined(Memory.rooms[room]) or _.isUndefined(Memory.rooms[room].num_sources):
                continue

            room_hauls = _.filter(rhauls, lambda m: m['data'].haul_room == room)
            if len(room_hauls) < Memory.rooms[room].num_sources:
                taken = [m['data'].source_id for m in room_hauls]

                for sid in Memory.rooms[room].sources:
                    if not taken.includes(sid):
                        self.launch_child_process('remotehaul', {'room_name': self._data.room_name,
                                                                 'haul_room': room,
                                                                 'source_id': sid})
    
    def launch_claims(self, to_claim: List[str]) -> None:
        claims = self.scheduler.proc_by_name('claim', self._pid)
        if len(claims) < len(to_claim):
            taken = [c['data'].target_room for c in claims]

            for target_room in to_claim:
                if not _.isUndefined(Game.rooms[target_room]) and Game.rooms[target_room].is_city():
                    self.room.memory.to_claim = list(self.room.memory.to_claim)[1:]
                    continue  # Room has already been claimed

                if not taken.includes(target_room):
                    proc_data = {
                        'room_name': self._data.room_name,
                        'target_room': target_room
                    }
                    self.launch_child_process('claim', proc_data)

    def launch_remote_work(self, to_work: List[str]) -> None:
        works = self.scheduler.proc_by_name('remotework', self._pid)
        if len(works) < len(to_work):
            taken = [m['data'].target_room for m in works]

            for target_room in to_work:
                if not _.isUndefined(Game.rooms[target_room]) and Game.rooms[target_room].rcl >= 3:
                    self.room.memory.to_work = list(self.room.memory.to_work)[1:]
                    continue

                if not taken.includes(target_room):
                    proc_data = {
                        'room_name': self._data.room_name,
                        'target_room': target_room
                    }
                    self.launch_child_process('remotework', proc_data)
    
    def launch_scouts(self, to_scout: List[str]) -> None:
        scouts = self.scheduler.proc_by_name('scout', self._pid)
        if len(scouts) < 1:
            taken = [s['data'].target_room for s in scouts]  # Possibly allow multiple simultaneous later

            for target_room in to_scout:
                if not taken.includes(target_room):
                    proc_data = {
                        'room_name': self._data.room_name,
                        'target_room': target_room
                    }
                    self.launch_child_process('scout', proc_data)

                    # print("Launching for", target_room)
                    self.room.memory.to_scout = list(self.room.memory.to_scout)[1:]
                    # print(self.room.memory.to_scout)
                    return  # only 1 thansk
