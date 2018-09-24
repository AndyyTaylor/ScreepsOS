
from defs import *  # noqa
from typing import cast

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class MineralSite(CreepProcess):

    def __init__(self, pid, data={}):
        super().__init__('mineralsite', pid, 2, data)

        if pid != -1:
            self.room = Game.rooms[self._data.room_name]
            self.mineral = Game.getObjectById(self._data.mineral_id)

    def _run(self):
        if _.isUndefined(self._data.has_init):
            self.init()

        self.run_creeps()

    def run_creep(self, creep):
        self.move_to_drop(creep)

        if creep.is_idle():
            creep.set_task('harvest', {'source_id': self._data.mineral_id})

        creep.run_current_task()

    def move_to_drop(self, creep):
        if creep.pos.x == self._data.drop_x and creep.pos.y == self._data.drop_y:
            return

        is_empty = len(self.room.lookForAt(LOOK_CREEPS, self._data.drop_x, self._data.drop_y)) == 0
        if is_empty:
            creep.set_task('travel', {'dest_x': self._data.drop_x, 'dest_y': self._data.drop_y,
                                      'dest_room_name': self._data.room_name})

    def needs_creeps(self):
        if not self._data.has_extractor:
            return False

        mineral = Game.getObjectById(self._data.mineral_id)
        if _.isNull(mineral) or mineral.mineralAmount == 0:
            return False

        return len(self._data.creep_names) < 1

    def is_valid_creep(self, creep):
        return creep.getActiveBodyparts(WORK) > 10 and creep.getActiveBodyparts(CARRY) < 1 and \
            _.isUndefined(creep.memory.remote)

    def gen_body(self, energyAvailable):
        body = [WORK, WORK, MOVE]
        mod = [WORK, WORK, MOVE]
        total_work = 2

        while self.get_body_cost(body.concat(mod)) <= energyAvailable and total_work < 15:
            total_work += 2
            body = body.concat(mod)

        return body, None

    def init(self):  # This should request certain buildings. container / link etc
        self._data.has_init = True

        pos = self.mineral.pos

        deposit_id = None
        x, y = pos.x, pos.y

        terrain = self.room.lookForAtArea(LOOK_TERRAIN, pos.y - 1, pos.x - 1,
                                          pos.y + 1, pos.x + 1, True)

        deposit_id = None
        drop_pos = None
        for tile in terrain:
            if tile.terrain != 'wall':
                drop_pos = {'x': tile.x, 'y': tile.y}
                break

        nearby_structs = self.room.lookForAtArea(LOOK_STRUCTURES, y - 1, x - 1, y + 1, x + 1, True)
        for struct in nearby_structs:
            if struct.structure.structureType == STRUCTURE_CONTAINER:
                deposit_id = struct.structure.id

        if deposit_id is None and len(self._data.build_tickets) < 1:
            nearby_terrain = self.room.lookForAtArea(LOOK_TERRAIN, y - 1, x - 1, y + 1, x + 1, True)
            for terrain in nearby_terrain:
                if terrain.terrain != 'wall':
                    print('container', terrain.x, terrain.y)
                    tid = self.ticketer.add_ticket('build', self._pid, {'type': STRUCTURE_CONTAINER,
                                                                        'x': terrain.x,
                                                                        'y': terrain.y,
                                                                        'city': self._data.room_name
                                                                        })
                    self._data.build_tickets.append(tid)

                    break
        elif deposit_id is not None:
            drop_pos = Game.getObjectById(deposit_id).pos
            self._data.drop_type = 'container'

        if not _.isUndefined(self.room.storage):
            start = self.room.storage.pos
            result = PathFinder.search(self.mineral.pos, {'pos': start, 'range': 7},
                                                         {'roomCallback': lambda r:
                                                          self.room.basic_matrix(True)})
            if not result.incomplete:
                for tile in result.path:
                    if tile.x == 0 or tile.x == 49 or tile.y == 0 or tile.y == 49:
                        continue

                    ticket = {
                        'type': STRUCTURE_ROAD,
                        'x': tile.x,
                        'y': tile.y,
                        'city': tile.roomName
                    }
                    self.ticketer.add_ticket('build', self._pid, ticket)

        has_extractor = False
        structs = self.room.lookForAt(LOOK_STRUCTURES, self.mineral)
        for struct in structs:
            if struct.structureType == STRUCTURE_EXTRACTOR:
                has_extractor = True
                break

        if not has_extractor:
            ticket = {
                'type': STRUCTURE_EXTRACTOR,
                'x': self.mineral.pos.x,
                'y': self.mineral.pos.y,
                'city': self._data.room_name
            }
            self.ticketer.add_ticket('build', self._pid, ticket)

        self._data.drop_x = drop_pos.x
        self._data.drop_y = drop_pos.y
        self._data.has_extractor = has_extractor
