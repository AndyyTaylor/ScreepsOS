
from defs import *  # noqa
from base import base

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class FeedSite(CreepProcess):

    def __init__(self, pid, data={}):
        super().__init__('feedsite', pid, 5, data)

    def _run(self):
        self.room = Game.rooms[self._data.room_name]
        self.controller = self.room.controller

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
        creep.say("Feeder")
        if creep.is_idle():
            if creep.is_empty():
                creep.set_task('gather')
            elif not creep.room.is_full():
                creep.set_task('feed')
            else:
                creep.set_task('travel', {'dest_x': self._data.hold_x,
                                          'dest_y': self._data.hold_y,
                                          'dest_room_name': self._data.room_name})

        creep.run_current_task()

    def needs_creeps(self):
        return len(self._data.creep_names) < 1

    def init(self):
        base_flag = Game.flags[self._data.room_name]
        feed_path = base['feedpaths'][self._data.index]

        if not base_flag:
            return

        self._data.hold_x = base_flag.pos.x + feed_path['hold_x']
        self._data.hold_y = base_flag.pos.y + feed_path['hold_y']

        self._data.has_init = True

    def place_flag(self):
        flags = self.room.flags

        x, y = self._data.hold_x, self._data.hold_y

        already_placed = False
        for flag in flags:
            if flag['name'] == 'FeedSite(' + str(x) + ',' + str(y) + ')':
                already_placed = True
                break

        if not already_placed:
            self.room.createFlag(x, y, 'FeedSite(' + str(x) + ',' + str(y) + ')', COLOR_GREEN)
