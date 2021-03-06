
import random
from defs import *  # noqa

from framework.process import Process
from base import base

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')
__pragma__('noalias', 'get')


class RoomPlanner(Process):

    def __init__(self, pid, data={}):
        super().__init__('roomplanner', pid, 3, data)

    def _run(self):
        self.room = Game.rooms[self._data.room_name]
        self.vis = self.room.visual

        self.load_base_pos()

        self.vis_enabled = True
        #
        # self.lay_structures(STRUCTURE_EXTENSION)
        # self.lay_structures(STRUCTURE_SPAWN)
        # self.lay_structures(STRUCTURE_TOWER)
        # self.lay_structures(STRUCTURE_ROAD)
        # self.lay_structures(STRUCTURE_TERMINAL)
        # self.lay_structures(STRUCTURE_LAB)
        # self.lay_structures(STRUCTURE_CONTAINER)
        #

        if Object.keys(js_global.WALL_WIDTH).includes(str(self.room.rcl)):
            self.visualise_walls(js_global.WALL_WIDTH[str(self.room.rcl)])

        #
        # # tickets = self.ticketer.get_tickets_by_type('build')
        # # for ticket in tickets:
        # #     self.build(ticket['data']['type'], int(ticket['data']['x']),
        # #                int(ticket['data']['y']), False)
        # #     print(int(ticket['data']['x']), int(ticket['data']['y']))
        self.vis_enabled = False

        has_laid = False
        if len(self.room.construction_sites) < 1:
            for type in js_global.BUILD_ORDER:
                if type == STRUCTURE_ROAD and self.room.rcl < js_global.ROAD_RCL:
                    continue

                if type == STRUCTURE_RAMPART:
                    if Object.keys(js_global.WALL_WIDTH).includes(str(self.room.rcl)):
                        self.visualise_walls(js_global.WALL_WIDTH[str(self.room.rcl)])

                        if not _.isUndefined(self.room.storage):
                            if self.room.can_place_wall() and self.room.storage.store.energy > js_global.STORAGE_MAX[
                                    self.room.rcl]:
                                self.room.memory.walls.hits += js_global.WALL_REINFORCEMENT

                if self.lay_structures(type):
                    has_laid = True
                    break

        for name in self._data.remotes:
            room = Game.rooms[name]
            if _.isUndefined(room) or len(room.construction_sites) > 10:
                continue

            if self.lay_structures(STRUCTURE_ROAD, name):
                has_laid = True
            elif self.lay_structures(STRUCTURE_CONTAINER, name):
                has_laid = True

        if not has_laid and len(self.room.construction_sites) == 0:
            self.sleep(300 + random.randint(0, 10))
        else:
            self.sleep(random.randint(0, 30))

    def lay_structures(self, type, room_name=None):
        if room_name is None:
            room_name = self._data.room_name

        if room_name == self._data.room_name:
            if Object.keys(base['buildings']).includes(type):
                positions = base['buildings'][type]['pos']
                for pos in positions:
                    if self.build(type, pos['x'] - 1, pos['y'] - 1):
                        return True

        tickets = _.filter(self.ticketer.get_tickets_by_type("build", room_name),
                           lambda t: t['data']['type'] == type)

        for ticket in tickets:
            if self.build(type, ticket['data']['x'], ticket['data']['y'], False, room_name):
                return True
            else:
                self.ticketer.delete_ticket(ticket['tid'])

        return False

    def build(self, type, x, y, add_base=True, room_name=None):
        if room_name is None:
            room_name = self._data.room_name

        if add_base:
            x += self._data.base_x
            y += self._data.base_y

        # TODO: Should return whether lay was successful
        if self.vis_enabled:
            self.draw_visual(x, y, type)

            return False
        else:
            if type == STRUCTURE_ROAD:
                terrain = Game.map.getRoomTerrain(room_name)
                if terrain.js_get(x, y) == TERRAIN_MASK_WALL:
                    return False

            res = Game.rooms[room_name].createConstructionSite(x, y, type)
            if res == ERR_INVALID_TARGET:
                creeps = Game.rooms[room_name].lookForAt(LOOK_CREEPS, x, y)
                if len(creeps) > 0:
                    structs = Game.rooms[room_name].lookForAt(LOOK_STRUCTURES, x, y)
                    for struct in structs:
                        if struct.structureType == type:
                            return False

                    res = OK

            return res == OK

    def draw_visual(self, x, y, type):
        structures = self.room.lookForAt(LOOK_STRUCTURES, x, y)
        for structure in structures:
            if structure.structureType == type:
                return

        if type == STRUCTURE_EXTENSION:
            self.draw_extension(x, y)
        elif type == STRUCTURE_SPAWN:
            self.draw_spawn(x, y)
        elif type == STRUCTURE_TOWER:
            self.draw_tower(x, y)
        elif type == STRUCTURE_ROAD:
            self.draw_road(x, y)
        elif type == STRUCTURE_TERMINAL:
            self.draw_terminal(x, y)
        elif type == STRUCTURE_LAB:
            self.draw_lab(x, y)
        else:
            self.draw_generic(x, y)

    def draw_extension(self, x, y):
        self.vis.circle(x, y, {'fill': 'yellow', 'radius': 0.3})

    def draw_spawn(self, x, y):
        self.vis.circle(x, y, {'fill': 'yellow', 'radius': 0.4})

    def draw_tower(self, x, y):
        self.vis.rect(x - 0.4, y - 0.4, 0.8, 0.8, {'fill': 'black'})

    def draw_road(self, x, y):
        self.vis.circle(x, y, {'fill': 'gray', 'radius': 0.4})

    def draw_terminal(self, x, y):
        self.vis.rect(x - 0.4, y - 0.4, 0.8, 0.8, {'fill': 'lightgray'})

    def draw_lab(self, x, y):
        self.vis.circle(x, y, {'fill': 'black', 'radius': 0.4})

    def draw_generic(self, x, y):
        self.vis.circle(x, y)

    def load_base_pos(self):
        if _.isUndefined(self._data.base_x) or _.isUndefined(self._data.base_y):
            for flag in self.room.flags:
                if flag['name'] == self._data.room_name:
                    self._data.base_x = flag.pos.x
                    self._data.base_y = flag.pos.y
                    return

            # If no flag exists
            self.place_base()

    def visualise_walls(self, width):
        start_x = self._data.base_x - 1
        start_y = self._data.base_y - 1

        width -= 1

        room = Game.rooms[self._data.room_name]
        terrain = room.getTerrain()

        if _.isUndefined(room.memory.walls):
            room.memory.walls = {}

        if _.isUndefined(room.memory.walls.last_placed):
            room.memory.walls.last_placed = 0

        if _.isUndefined(room.memory.walls.hits):
            room.memory.walls.hits = js_global.WALL_HITS

        for xx in range(start_x, start_x + base['width'] + 3):
            for yy in range(start_y, start_y + base['height'] + 3):
                if min(abs(start_x - xx), abs(start_x + base['width'] + 2 - xx)) > width and \
                        min(abs(start_y - yy), abs(start_y + base['height'] + 2 - yy)) > width or \
                        terrain.get(xx, yy) == TERRAIN_MASK_WALL:
                    continue

                if self.vis_enabled:
                    self.vis.rect(xx - 0.5, yy - 0.5, 1, 1, {'fill': 'green', 'opacity': 0.3})
                else:
                    if room.can_place_wall():
                        if room.createConstructionSite(xx, yy, STRUCTURE_RAMPART) == OK:
                            room.memory.walls.last_placed = Game.time
                    else:
                        structs = room.lookForAt(LOOK_STRUCTURES, xx, yy)
                        placed = False
                        for struct in structs:
                            if struct.structureType == STRUCTURE_RAMPART:
                                placed = True
                                break

                        if not placed:
                            self.vis.rect(xx - 0.5, yy - 0.5, 1, 1, {'fill': 'blue', 'opacity': 0.3})

    def place_base(self):
        valid = [[True for y in range(50)] for x in range(50)]

        width = base['width']
        height = base['height']
        for x in range(50):
            for y in range(50):
                if self.is_wall(x, y) or x == 0 or y == 0 or x == 49 or y == 49:
                    for w in range(min(width + 1, x + 1)):
                        for h in range(min(height + 1, y + 1)):
                            valid[x - w][y - h] = False

        valid_pos = []
        for x in range(50):
            for y in range(50):
                if valid[x][y]:
                    valid_pos.append({'x': x, 'y': y})

        best_pos = None
        best_score = None
        for pos in valid_pos:
            score = (- abs(pos['x'] - 20) - abs(pos['y'] - 20))  # Want base centered, not flag
            if best_pos is None or score > best_score:
                best_pos = pos
                best_score = score

        self._data.base_x = best_pos['x']
        self._data.base_y = best_pos['y']
        self.room.createFlag(best_pos['x'], best_pos['y'], self._data.room_name, COLOR_WHITE)

        for x in range(len(valid)):
            for y in range(len(valid[0])):
                if x == best_pos['x'] and y == best_pos['y']:
                    self.vis.rect(x - 0.5, y - 0.5, 1, 1, {'fill': '#00FF00'})
                elif valid[x][y]:
                    self.vis.rect(x - 0.5, y - 0.5, 1, 1, {'fill': '#0000FF'})
                else:
                    self.vis.rect(x - 0.5, y - 0.5, 1, 1, {'fill': '#FF0000'})

    def is_wall(self, x, y):
        terrain = self.room.lookForAt(LOOK_TERRAIN, x, y)

        return terrain == 'wall'
