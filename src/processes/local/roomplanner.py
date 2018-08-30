
from defs import *  # noqa

from framework.process import Process
from base import base

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class RoomPlanner(Process):

    def __init__(self, pid, data={}):
        super().__init__('roomplanner', pid, 4, data)

    def _run(self):
        self.room = Game.rooms[self._data.room_name]
        self.vis = self.room.visual

        self.load_base_pos()

        self.vis_enabled = True

        self.lay_structures(STRUCTURE_EXTENSION)
        self.lay_structures(STRUCTURE_SPAWN)
        self.lay_structures(STRUCTURE_TOWER)
        self.lay_structures(STRUCTURE_ROAD)
        self.lay_structures(STRUCTURE_TERMINAL)
        self.lay_structures(STRUCTURE_LAB)

        ticket = self.ticketer.get_highest_priority('build')
        if ticket:
            self.build(ticket['data']['type'], int(ticket['data']['x']),
                       int(ticket['data']['y']), False)

        self.vis_enabled = False

        if len(self.room.construction_sites) < 1:
            for type in js_global.BUILD_ORDER:
                if self.lay_structures(type):
                    break

    def lay_structures(self, type):
        positions = base['buildings'][type]['pos']
        for pos in positions:
            if self.build(type, pos['x'] - 1, pos['y'] - 1):
                return True

    def build(self, type, x, y, add_base=True):
        if add_base:
            x += self._data.base_x
            y += self._data.base_y

        # TODO: Should return whether lay was successful
        if self.vis_enabled:
            self.draw_visual(x, y, type)

            return False
        else:
            return self.room.createConstructionSite(x, y, type) == OK

    def draw_visual(self, x, y, type):
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
