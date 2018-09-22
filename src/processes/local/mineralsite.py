
from defs import *  # noqa

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

        print("Mineral site running")

        self.run_creeps()

    def run_creep(self, creep):
        creep.say("Harvest mineral")

        creep.run_current_task()

    def needs_creeps(self):
        if _.isUndefined(self._data.extractor_id):
            return False

        return len(self._data.creep_names) < 1

    def is_valid_creep(self, creep):
        return creep.getActiveBodyparts(WORK) > 0 and creep.getActiveBodyparts(CARRY) < 1 and \
            _.isUndefined(creep.memory.remote)

    def gen_body(self, energyAvailable):
        body = [WORK, WORK, MOVE]
        mod = [WORK, WORK, MOVE]
        total_work = 1

        while self.get_body_cost(body.concat(mod)) <= energyAvailable and total_work < 6:
            total_work += 1
            body = body.concat(mod)

        return body, None

    def init(self):  # This should request certain buildings. container / link etc
        self._data.has_init = True

        pos = self.mineral.pos
        print(self._data.mineral_id, pos)

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

                    self.ticketer.add_ticket('build', self._pid, {'type': STRUCTURE_ROAD,
                                                                  'x': tile.x,
                                                                  'y': tile.y,
                                                                  'city': tile.roomName
                                                                  })

        self._data.drop_x = drop_pos.x
        self._data.drop_y = drop_pos.y
