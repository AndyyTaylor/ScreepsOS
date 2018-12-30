
from defs import *  # noqa
# from extends import *  # noqa
from base import base

from framework.process import Process

__pragma__('noalias', 'keys')


class City(Process):

    def __init__(self, pid: int, data=None) -> None:
        super().__init__("city", pid, 1, data)

    def _run(self) -> None:
        self.room: Room = Game.rooms[self._data.main_room]

        self.validate_room_memory()

        self.launch_feed_sites()
        self.launch_build_sites()
        self.launch_repair_sites()
        self.launch_mining_sites()
        self.launch_one_of_processes()

    def launch_one_of_processes(self) -> None:
        """ Launch one-of processes for the main room """
        one_of = ['roomplanner', 'spawning', 'defence', 'upgradesite']

        if self.room.rcl >= 4 and not _.isUndefined(self.room.storage):
            one_of.append('logistics')
            one_of.append('remote')

        if self.room.rcl >= 5:
            one_of.append('management')

        if len(self.room.damaged_walls) > 0:
            one_of.append('wallrepair')

        for name in one_of:
            # TODO: Just load remotes in the process itself
            if self.scheduler.count_by_name(name, self._pid) < 1:
                self.launch_child_process(name, {'room_name': self._data.main_room,
                                                 'remotes': self.room.memory.remotes})

    def launch_feed_sites(self) -> None:
        """ Launch the needed feed sites for the room """
        # ? Can I replace this with reduce, or some other python equiv
        assert isinstance(base['feedpaths'], list)  # mypy can't work out the type of this
        needed_paths = _.filter(base['feedpaths'], lambda p: p['rcl'] <= self.room.rcl)

        if self.scheduler.count_by_name('feedsite', self._pid) < len(needed_paths):
            taken_paths = []
            for proc in self.scheduler.proc_by_name('feedsite', self._pid):
                taken_paths.append(proc['data'].index)

            for path in range(len(needed_paths)):
                if not taken_paths.includes(path):
                    self.launch_child_process('feedsite', {'room_name': self._data.main_room, 'index': path})

    def launch_build_sites(self) -> None:
        """ Launch a build site for each construction site in the room """
        num_buildsites = self.scheduler.count_by_name('buildsite', self._pid)
        if num_buildsites < len(self.room.construction_sites):
            taken_ids = []
            for proc in self.scheduler.proc_by_name('buildsite', self._pid):
                taken_ids.append(proc['data'].site_id)

            site_ids = [site.id for site in self.room.construction_sites]
            for site_id in site_ids:  # ? Can this also be replaced with reduce or something?
                if not taken_ids.includes(site_id):
                    self.launch_child_process('buildsite', {'room_name': self._data.main_room,
                                                            'site_id': site_id})

    def launch_repair_sites(self) -> None:
        """ Launch repair process for room.repair_sites[0] """
        if self.scheduler.count_by_name('repairsite', self._pid) < 1 and len(self.room.repair_sites) > 0:
            proc_data = {
                'room_name': self._data.main_room,
                'site_id': self.room.repair_sites[0].id
            }

            self.launch_child_process('repairsite', proc_data)
    
    def launch_mining_sites(self) -> None:
        """ Launch minesites and mineralsites for the room """
        sources = self.room.sources

        if self.scheduler.count_by_name('minesite', self._pid) < len(sources):
            taken_ids = []
            for proc in self.scheduler.proc_by_name('minesite', self._pid):
                taken_ids.append(proc['data'].source_id)

            source_ids = [source.id for source in sources]
            for source_id in source_ids:
                if not taken_ids.includes(source_id):
                    proc_data = {
                        'room_name': self._data.main_room,
                        'source_id': source_id             
                    }
                    self.launch_child_process('minesite', proc_data)

        if self.scheduler.count_by_name('mineralsite', self._pid) < 1 and self.room.rcl >= 6:
            proc_data = {
                'room_name': self._data.main_room,
                'mineral_id': self.room.mineral.id    
            }
            self.launch_child_process('mineralsite', proc_data)

    def validate_room_memory(self) -> None:
        """ Validates the main room's .memory """

        # Room data
        if _.isUndefined(self.room.memory):
            self.room.memory = {}

        if _.isUndefined(self.room.memory.towers):
            self.room.memory.towers = {'attack': 0, 'heal': 0, 'repair': 0}

        if _.isUndefined(self.room.memory.walls):
            self.room.memory.walls = {'last_updated': 0, 'hits': js_global.MIN_WALL_HITS}

        if _.isUndefined(self.room.memory.walls.hits) or self.room.memory.walls.hits < js_global.MIN_WALL_HITS:
            self.room.memory.walls.hits = js_global.MIN_WALL_HITS

        if _.isUndefined(self.room.memory.remotes):
            self.room.memory.remotes = []
        
        if _.isUndefined(self.room.memory.to_claim):
            self.room.memory.to_claim = []

        # Room stats
        if _.isUndefined(Memory.stats.rooms[self._data.main_room]):
            Memory.stats.rooms[self._data.main_room] = {}

        if _.isUndefined(Memory.stats.rooms[self._data.main_room].lharvest):
            Memory.stats.rooms[self._data.main_room].lharvest = {'spawn': 0, 'harvest': 0, 'transfer': 0}

        if _.isUndefined(Memory.stats.rooms[self._data.main_room].rharvest):
            Memory.stats.rooms[self._data.main_room].rharvest = {'spawn': 0, 'harvest': 0, 'transfer': 0}
