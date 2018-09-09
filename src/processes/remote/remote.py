
from defs import *  # noqa

from framework.process import Process

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class Remote(Process):

    def __init__(self, pid, data={}):
        super().__init__('remote', pid, 3, data)

    def _run(self):
        self.room = Game.rooms[self._data.room_name]

        should_mine = ['W58S2', 'W59S1']

        if self.scheduler.count_by_name('reserve', self._pid) < len(should_mine):
            is_reserving = []

            for proc in self.scheduler.proc_by_name('reserve', self._pid):
                is_reserving.append(proc['data'].target_room)

            for mine_room in should_mine:
                if not is_reserving.includes(mine_room):
                    self.launch_child_process('reserve', {'room_name': self._data.room_name,
                                                          'target_room': mine_room})

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

        rhauls = self.scheduler.proc_by_name('remotehaul', self._pid)
        for room in should_mine:
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

        # if self.scheduler.count_by_name('remotemine', self._pid) < len(should_mine):
            # is_mining = []
            #
            # for proc in self.scheduler.proc_by_name('remotemine', self._pid):
            #     is_mining.append(proc['data'].mine_room)
            #
            # for mine_room in should_mine:
            #     if not is_mining.includes(mine_room):
                    # self.launch_child_process('remotemine', {'room_name': self._data.room_name,
                    #                                          'mine_room': mine_room})
