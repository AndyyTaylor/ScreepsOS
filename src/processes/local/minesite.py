
from defs import *  # noqa

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class MineSite(CreepProcess):

    def __init__(self, pid, data={}):
        super().__init__('minesite', pid, 3, data)

    def _run(self):
        self.room = Game.rooms[self._data.room_name]
        self.source = Game.getObjectById(self._data.source_id)

        if _.isUndefined(self._data.has_init):
            self.init()

        self.place_flag()

        self.run_creeps()

    def run_creep(self, creep):
        if self._data.creep_names.indexOf(creep.js_name) == 0:
            empty = len(self.room.lookForAt(LOOK_CREEPS, self._data.drop_x, self._data.drop_y)) == 0
            if creep.is_idle() and (creep.pos.x != self._data.drop_x or
                                    creep.pos.y != self._data.drop_y) and empty:
                creep.set_task('travel', {'dest_x': self._data.drop_x, 'dest_y': self._data.drop_y,
                                          'dest_room_name': self._data.room_name})
        if creep.is_idle():
            creep.set_task('harvest', {'source_id': self._data.source_id})

        creep.run_current_task()

    def needs_creeps(self):
        total = 0
        for name in self._data.creep_names:
            creep = Game.creeps[name]
            if creep:
                total += creep.getActiveBodyparts(WORK)

        if total >= 6:
            return False

        if _.isUndefined(self._data.adj_tiles):
            return len(self._data.creep_names) < 1

        return len(self._data.creep_names) < self._data.adj_tiles

    def is_valid_creep(self, creep):
        return creep.getActiveBodyparts(WORK) > 0 and creep.getActiveBodyparts(CARRY) < 3

    def gen_body(self, energyAvailable):
        # Should have no carry before link, and get carry when link exists

        body = [WORK, MOVE]
        mod = [WORK, MOVE]
        total_work = 1

        while self.get_body_cost(body.concat(mod)) <= energyAvailable and total_work < 6:
            total_work += 1
            body = body.concat(mod)

        return body, None

    def init(self):  # This should request certain buildings. container / link etc
        self._data.has_init = True

        pos = self.source.pos
        terrain = self.room.lookForAtArea(LOOK_TERRAIN, pos.y - 1, pos.x - 1,
                                          pos.y + 1, pos.x + 1, True)

        deposit_id = None
        drop_pos = None
        adj_tiles = 0
        for tile in terrain:
            if tile.terrain != 'wall':
                adj_tiles += 1
                drop_pos = {'x': tile.x, 'y': tile.y}

        self._data.adj_tiles = adj_tiles
        self._data.drop_type = 'floor'

        x, y = pos.x, pos.y
        nearby_structs = self.room.lookForAtArea(LOOK_STRUCTURES, y - 1, x - 1, y + 1, x + 1, True)
        for struct in nearby_structs:
            if struct.structure.structureType == STRUCTURE_CONTAINER:
                deposit_id = struct.structure.id

        if deposit_id is None and len(self._data.build_tickets) < 1:
            nearby_terrain = self.room.lookForAtArea(LOOK_TERRAIN, y - 1, x - 1, y + 1, x + 1, True)
            for terrain in nearby_terrain:
                if terrain.terrain != 'wall':
                    tid = self.ticketer.add_ticket('build', self._pid, {'type': STRUCTURE_CONTAINER,
                                                                        'x': terrain.x,
                                                                        'y': terrain.y})
                    self._data.build_tickets.append(tid)

                    return
        else:
            drop_pos = Game.getObjectById(deposit_id).pos
            self._data.drop_type = 'container'

        self._data.drop_x = drop_pos.x
        self._data.drop_y = drop_pos.y

    def place_flag(self):
        flags = self.room.flags

        x, y = self.source.pos.x, self.source.pos.y

        already_placed = False
        for flag in flags:
            if flag['name'] == 'MineSite(' + str(x) + ',' + str(y) + ')':
                already_placed = True
                break

        if not already_placed:
            self.room.createFlag(x, y, 'MineSite(' + str(x) + ',' + str(y) + ')', COLOR_YELLOW)
