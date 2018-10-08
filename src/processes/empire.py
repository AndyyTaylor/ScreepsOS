
from defs import *  # noqa
from extends import *  # noqa
from base import base

from framework.process import Process

__pragma__('noalias', 'keys')


class Empire(Process):

    def __init__(self, pid, data={}):
        super().__init__("empire", pid, 1, data)

    def _run(self):
        self.launch_cities()

        # if self.scheduler.count_by_name('attackplanner') < 1:
        #     self.scheduler.launch_process('attackplanner', {'target_room': 'W51N2'})

    def launch_cities(self):
        cities = []

        for room_name in Object.keys(Game.rooms):
            room = Game.rooms[room_name]

            if room.is_city():
                cities.append(room_name)

        if self.scheduler.count_by_name('city') < len(cities):
            taken_cities = []
            for proc in self.scheduler.proc_by_name('city'):
                taken_cities.append(proc['data'].main_room)

            for city in cities:
                if not taken_cities.includes(city):
                    self.scheduler.launch_process('city', {'main_room': city})
