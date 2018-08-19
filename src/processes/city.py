
from defs import *  # noqa

from framework.process import Process

__pragma__('noalias', 'keys')


class City(Process):

    def __init__(self, pid, data={}):
        super().__init__("city", pid, 5, data)

    def _run(self):
        room = Game.rooms[self._data.main_room]

        sources = room.get_sources()

        if self.scheduler.count_by_name('roomplanner', self._pid) < 1:
            self.launch_child_process('roomplanner', {'room_name': self._data.main_room})

        if self.scheduler.count_by_name('minesite', self._pid) < len(sources):
            taken_ids = []
            source_ids = [source.id for source in sources]

            for proc in self.scheduler.proc_by_name('minesite', self._pid):
                taken_ids.append(proc['data'].source_id)

            for source_id in source_ids:
                if not taken_ids.includes(source_id):
                    self.launch_child_process('minesite', {'source_id': source_id,
                                                           'room_name': self._data.main_room})
