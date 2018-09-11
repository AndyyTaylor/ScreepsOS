
from defs import *  # noqa
from base import base

from framework.process import Process

__pragma__('noalias', 'keys')


class City(Process):

    def __init__(self, pid, data={}):
        super().__init__("city", pid, 1, data)

    def _run(self):
        room = Game.rooms[self._data.main_room]

        sources = room.get_sources()

        if self._data.main_room == 'W59S2':
            remotes = ['W58S2', 'W59S1']
        else:
            remotes = []

        one_of = ['roomplanner', 'spawning', 'defence', 'logistics']

        if room.rcl >= 5:
            one_of.append('management')
            one_of.append('remote')

        for name in one_of:
            if self.scheduler.count_by_name(name, self._pid) < 1:
                self.launch_child_process(name, {'room_name': self._data.main_room,
                                                 'remotes': remotes})

        needed_paths = _.filter(base['feedpaths'], lambda p: p['rcl'] <= room.rcl)
        if self.scheduler.count_by_name('feedsite', self._pid) < len(needed_paths):
            paths = [i for i in range(len(needed_paths))]
            taken_paths = []
            for proc in self.scheduler.proc_by_name('feedsite', self._pid):
                taken_paths.append(proc['data'].index)

            for path in paths:
                if not taken_paths.includes(path):
                    self.launch_child_process('feedsite', {'room_name': self._data.main_room,
                                                           'index': path})

        if self.scheduler.count_by_name('upgradesite', self._pid) < 1:
            self.launch_child_process('upgradesite', {'room_name': self._data.main_room})

        if self.scheduler.count_by_name('buildsite', self._pid) < len(room.construction_sites):
            taken_ids = []
            site_ids = [site.id for site in room.construction_sites]

            for proc in self.scheduler.proc_by_name('buildsite', self._pid):
                taken_ids.append(proc['data'].site_id)

            for site_id in site_ids:
                if not taken_ids.includes(source_id):
                    self.launch_child_process('buildsite', {'site_id': site_id,
                                                            'room_name': self._data.main_room})

        if self.scheduler.count_by_name('repairsite', self._pid) < 1 and len(room.repair_sites) > 0:
            self.launch_child_process('repairsite', {'site_id': room.repair_sites[0].id,
                                                     'room_name': self._data.main_room})

        if self.scheduler.count_by_name('minesite', self._pid) < len(sources):
            taken_ids = []
            source_ids = [source.id for source in sources]

            for proc in self.scheduler.proc_by_name('minesite', self._pid):
                taken_ids.append(proc['data'].source_id)

            for source_id in source_ids:
                if not taken_ids.includes(source_id):
                    self.launch_child_process('minesite', {'source_id': source_id,
                                                           'room_name': self._data.main_room})
