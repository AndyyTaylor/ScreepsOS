
from defs import *  # noqa

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class MineSite(CreepProcess):

    def __init__(self, pid, data={}):
        super().__init__('minesite', pid, 5, data)

    def _run(self):
        self.room = Game.rooms[self._data.room_name]
        self.source = Game.getObjectById(self._data.source_id)

        if _.isUndefined(self._data.has_init):
            self.init()

        self.place_flag()

        self.run_creeps()

    def run_creeps(self):
        expired_creeps = []
        for name in self._data.creep_names:
            creep = Game.creeps[name]

            if not creep:
                expired_creeps.append(name)
                continue

            self.run_creep(creep)

        for name in expired_creeps:
            self._data.creep_names.remove(name)

    def run_creep(self, creep):
        creep.set_task('harvest', {'source_id': self._data.source_id})
        creep.run_current_task()

    def needs_creeps(self):
        return len(self._data.creep_names) < self._data.adj_tiles

    def init(self):  # This should request certain buildings. container / link etc
        self._data.has_init = True

        pos = self.source.pos
        terrain = self.room.lookForAtArea(LOOK_TERRAIN, pos.y - 1, pos.x - 1,
                                          pos.y + 1, pos.x + 1, True)

        drop_pos = None
        adj_tiles = 0
        for tile in terrain:
            if tile.terrain != 'wall':
                adj_tiles += 1
                drop_pos = {'x': tile.x, 'y': tile.y}
        self._data.adj_tiles = adj_tiles

        structures = self.room.lookForAtArea(LOOK_STRUCTURES, pos.y - 1, pos.x - 1,
                                             pos.y + 1, pos.x + 1, True)
        for struct in structures:
            pass  # Comlete once I actually have structures

        self._data.drop_x = drop_pos.x
        self._data.drop_y = drop_pos.y
        self._data.drop_type = 'floor'

    def place_flag(self):
        flags = self.room.flags

        x, y = self.source.pos.x, self.source.pos.y

        already_placed = False
        for flag in flags:
            if flag['name'] == 'MineSite(' + str(x) + ',' + str(y) + ')':
                already_placed = True
                break

        if not already_placed:
            self.room.createFlag(x, y, 'MineSite(' + str(x) + ',' + str(y) + ')', COLOR_GREEN)
