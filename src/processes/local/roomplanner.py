
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
        if len(self.room.construction_sites) < 1:
            self.lay_structures(STRUCTURE_EXTENSION)

    def lay_structures(self, type):
        positions = base['buildings'][type]['pos']
        for pos in positions:
            if self.build(type, pos['x'] - 1, pos['y'] - 1):
                return True

    def build(self, type, x, y):
        x += self._data.base_x
        y += self._data.base_y

        # TODO: Should return whether lay was successful
        self.room.createConstructionSite(x, y, type)

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
            score = (- abs(pos['x'] - 25) - abs(pos['y'] - 25))
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
