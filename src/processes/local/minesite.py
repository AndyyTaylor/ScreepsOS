
from defs import *  # noqa
from typing import cast

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class MineSite(CreepProcess):

    def __init__(self, pid, data={}):
        super().__init__('minesite', pid, 2, data)

        if pid != -1:
            self.room = Game.rooms[self._data.room_name]
            self.source = Game.getObjectById(self._data.source_id)

    def _run(self):
        if _.isUndefined(self._data.has_init):
            self.init()

        self.run_creeps()

    def run_creep(self, creep):
        if self._data.creep_names.indexOf(creep.js_name) == 0:
            self.move_to_drop(creep)

        if creep.is_idle():
            creep.set_task('harvest', {'source_id': self._data.source_id})

        if self._data.drop_type == STRUCTURE_LINK:
            link = Game.getObjectById(self._data.deposit_id)
            if link.energy > 0 and link.cooldown == 0:
                link.transferEnergy(self.room.cent_link)

            if _.sum(creep.carry) + 12 >= creep.carryCapacity:  # Don't drop any resources
                if not creep.pos.isNearTo(link):
                    creep.moveTo(link)
                else:
                    creep.transfer(link, RESOURCE_ENERGY)

        creep.run_current_task()

    def move_to_drop(self, creep):
        if creep.pos.x == self._data.drop_x and creep.pos.y == self._data.drop_y:
            return

        is_empty = len(self.room.lookForAt(LOOK_CREEPS, self._data.drop_x, self._data.drop_y)) == 0
        if is_empty:
            creep.set_task('travel', {'dest_x': self._data.drop_x, 'dest_y': self._data.drop_y,
                                      'dest_room_name': self._data.room_name})

    def needs_creeps(self):
        total = 0
        for name in self._data.creep_names:
            creep = Game.creeps[name]
            if creep:
                total += creep.getActiveBodyparts(WORK)

        if total >= 5:
            return False

        if _.isUndefined(self._data.adj_tiles):
            return len(self._data.creep_names) < 1

        return len(self._data.creep_names) < self._data.adj_tiles

    def is_valid_creep(self, creep):
        if self.get_ideal_deposit() == STRUCTURE_LINK:
            return creep.getActiveBodyparts(WORK) > 0 and creep.getActiveBodyparts(CARRY) > 0 and \
                creep.getActiveBodyparts(CARRY) < 5 and creep.getActiveBodyparts(WORK) < 10 and \
                _.isUndefined(creep.memory.remote)
        else:
            return creep.getActiveBodyparts(WORK) > 0 and creep.getActiveBodyparts(CARRY) == 0 and \
                creep.getActiveBodyparts(WORK) < 10 and _.isUndefined(creep.memory.remote)

    def gen_body(self, energyAvailable):
        mod = [WORK, WORK, MOVE]
        total_work = 2

        if self.get_ideal_deposit() == STRUCTURE_LINK:
            body = [WORK, CARRY, MOVE]
        else:
            body = [WORK, WORK, MOVE]

        while self.get_body_cost(body.concat(mod)) <= energyAvailable and total_work < 6:
            total_work += 2
            body = body.concat(mod)

        if total_work == 5 and self.get_ideal_deposit() == STRUCTURE_LINK:
            body = body.concat([WORK, MOVE])

        return body, None

    def init(self):
        self._data.has_init = True

        drop_pos, drop_type = self.load_terrain()
        drop_pos, drop_type, deposit_id = self.load_deposit(drop_pos, drop_type)

        ideal_deposit = self.get_ideal_deposit()
        if self._data.room_name == 'W51S1' or self._data.room_name == 'W59S2':
            if deposit_id is None or drop_type != ideal_deposit:
                if deposit_id is not None:
                    Game.getObjectById(deposit_id).destroy()

                    deposit_id = None
                    drop_type = 'floor'

                if ideal_deposit == STRUCTURE_LINK:
                    self.build_link(drop_pos)
                else:
                    self.build_container(drop_pos)

        # Build to room.center instead
        if not _.isUndefined(self.room.storage):
            start = self.room.storage.pos
            result = PathFinder.search(self.source.pos, {'pos': start, 'range': 7},
                                                        {'roomCallback': lambda r:
                                                         self.room.basic_matrix(True)})
            if not result.incomplete:
                for tile in result.path:
                    if tile.x == 0 or tile.x == 49 or tile.y == 0 or tile.y == 49:
                        continue

                    self.ticketer.add_ticket('build', self._pid, {'type': STRUCTURE_ROAD,
                                                                  'x': tile.x,
                                                                  'y': tile.y,
                                                                  'city': tile.roomName
                                                                  })

        self._data.drop_x = drop_pos.x
        self._data.drop_y = drop_pos.y
        self._data.drop_type = drop_type
        self._data.deposit_id = deposit_id

    def load_terrain(self):
        adj_tiles = 0
        drop_pos = None
        pos = self.source.pos
        terrain = self.room.lookForAtArea(LOOK_TERRAIN, pos.y - 1, pos.x - 1,
                                          pos.y + 1, pos.x + 1, True)
        structs = self.room.lookForAtArea(LOOK_STRUCTURES, pos.y - 1, pos.x - 1,
                                          pos.y + 1, pos.x + 1)

        for tile in terrain:
            if tile.terrain != 'wall':
                walkable = True
                for struct in structs[tile.y][tile.x]:
                    type = struct.structureType
                    if type != STRUCTURE_ROAD and type != STRUCTURE_CONTAINER:
                        walkable = False
                        break

                if walkable:
                    adj_tiles += 1
                    drop_pos = {'x': tile.x, 'y': tile.y}

        self._data.adj_tiles = adj_tiles

        return drop_pos, 'floor'

    def load_deposit(self, drop_pos, drop_type):
        deposit_id = None
        x, y = self.source.pos.x, self.source.pos.y
        nearby_structs = self.room.lookForAtArea(LOOK_STRUCTURES, y - 2, x - 2, y + 2, x + 2, True)
        for struct in nearby_structs:
            type = struct.structure.structureType
            if type == STRUCTURE_LINK or (type == STRUCTURE_CONTAINER and deposit_id is None):
                deposit_id = struct.structure.id
                drop_type = type

        if deposit_id is not None and drop_type != STRUCTURE_LINK:
            drop_pos = Game.getObjectById(deposit_id).pos
        elif drop_type == STRUCTURE_LINK:
            pos = self.source.pos
            link = Game.getObjectById(deposit_id)
            terrain = self.room.lookForAtArea(LOOK_TERRAIN, pos.y - 1, pos.x - 1,
                                              pos.y + 1, pos.x + 1, True)
            for tile in terrain:
                if tile.terrain == 'wall':
                    continue

                tpos = __new__(RoomPosition(tile.x, tile.y, self._data.room_name))
                if tpos.getRangeTo(link) == 1:
                    drop_pos = tpos
                    break

        return drop_pos, drop_type, deposit_id

    def get_ideal_deposit(self):
        if self.room.rcl < 6:
            return STRUCTURE_CONTAINER
        elif self.room.rcl > 6:
            return STRUCTURE_LINK
        else:
            furthest_dist = 0
            is_furthest = False

            for source in self.room.sources:
                dist = self.room.center.getRangeTo(source)  # Replace with path
                if dist > furthest_dist:                    # once I sort out costmatrices
                    furthest_dist = dist
                    is_furthest = (source == self.source)

            if is_furthest:
                return STRUCTURE_LINK
            else:
                return STRUCTURE_CONTAINER

    def build_link(self, pos):
        x, y = pos.x, pos.y
        nearby_terrain = self.room.lookForAtArea(LOOK_TERRAIN, y - 1, x - 1, y + 1, x + 1, True)

        for terrain in nearby_terrain:
            if terrain.terrain != 'wall' and (terrain.x != x or terrain.y != y):
                ticket = {
                    'type': STRUCTURE_LINK,
                    'x': terrain.x,
                    'y': terrain.y,
                    'city': self._data.room_name
                }
                tid = self.ticketer.add_ticket('build', self._pid, ticket)
                self._data.build_tickets.append(tid)

                break

    def build_container(self, pos):
        ticket = {
            'type': STRUCTURE_CONTAINER,
            'x': pos.x,
            'y': pos.y,
            'city': self._data.room_name
        }
        tid = self.ticketer.add_ticket('build', self._pid, ticket)
        self._data.build_tickets.append(tid)
