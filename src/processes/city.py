
from defs import *  # noqa
from extends import *  # noqa
from base import base

from framework.process import Process

__pragma__('noalias', 'keys')


class City(Process):

    def __init__(self, pid, data={}):
        super().__init__("city", pid, 1, data)

    def _run(self):
        room = Game.rooms[self._data.main_room]

        if _.isUndefined(room.memory.towers):
            room.memory.towers = {'attack': 0, 'heal': 0, 'repair': 0}

        if _.isUndefined(room.memory.walls):
            room.memory.walls = {'last_updated': 0, 'hits': js_global.MIN_WALL_HITS}

        if _.isUndefined(room.memory.walls.hits) or room.memory.walls.hits < js_global.MIN_WALL_HITS:
            room.memory.walls.hits = js_global.MIN_WALL_HITS

        if _.isUndefined(Memory.stats.rooms[self._data.main_room]):
            Memory.stats.rooms[self._data.main_room] = {}

        if _.isUndefined(Memory.stats.rooms[self._data.main_room].lharvest):
            Memory.stats.rooms[self._data.main_room].lharvest = {'spawn': 0, 'harvest': 0, 'transfer': 0}

        if _.isUndefined(Memory.stats.rooms[self._data.main_room].rharvest):
            Memory.stats.rooms[self._data.main_room].rharvest = {'spawn': 0, 'harvest': 0, 'transfer': 0}

        sources = room.get_sources()

        if self.scheduler.count_by_name('dismantle', self._pid) < 1 and \
                (self._data.main_room == 'W59S2'):
            self.launch_child_process('dismantle', {'room_name': self._data.main_room,
                                                    'target_room': 'W51N1'})

        if self.scheduler.count_by_name('sappattack', self._pid) < 1 and \
                (self._data.main_room == 'W48N1' or self._data.main_room == 'W51S1' or self._data.main_room == 'W56N1'
                or self._data.main_room == 'W59N2'):
            self.launch_child_process('sappattack', {'room_name': self._data.main_room,
                                                     'target_room': 'W51N1'})

        if self._data.main_room == 'W59S2':
            remotes = ['W58S2', 'W59S1', 'W58S1']
        elif self._data.main_room == 'W51S1':
            remotes = ['W51S2']
        elif self._data.main_room == 'W59N2':
            remotes = ['W59N1']
        elif self._data.main_room == 'W53N5':
            remotes = ['W53N4']
        elif self._data.main_room == 'W54N2':
            remotes = ['W55N2']
        elif self._data.main_room == 'W51N5':
            remotes = ['W51N6']
        elif self._data.main_room == 'W53N7':
            remotes = ['W54N7']
        elif self._data.main_room == 'W48N1':
            remotes = ['W48N2']
        else:
            remotes = []

        one_of = ['roomplanner', 'spawning', 'defence']

        if room.rcl >= 4 and not _.isUndefined(room.storage):
            one_of.append('logistics')
            one_of.append('remote')

        if room.rcl >= 5:
            one_of.append('management')

        if len(room.damaged_walls) > 0:
            one_of.append('wallrepair')

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
                if not taken_ids.includes(site_id):
                    self.launch_child_process('buildsite', {'site_id': site_id,
                                                            'room_name': self._data.main_room})

        if self.scheduler.count_by_name('repairsite', self._pid) < 1 and \
                len(room.repair_sites) > 0:
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

        if self.scheduler.count_by_name('mineralsite', self._pid) < 1 and room.rcl >= 6:
            self.launch_child_process('mineralsite', {'mineral_id': room.mineral.id,
                                                      'room_name': self._data.main_room})
