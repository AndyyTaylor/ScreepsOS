
from defs import *  # noqa

from framework.scheduler import Scheduler

__pragma__('noalias', 'keys')


class Kernel():

    def __init__(self):
        self.validate_memory()

        self.scheduler = Scheduler()

        new_upload = self.check_version()
        if new_upload:
            self.scheduler.kill_all_processes()

    def start(self):
        self.launch_cities()  # Launch Empire

        self.scheduler.queue_processes()

    def run(self):
        process = self.scheduler.get_next_process()

        while process is not None:
            # print("Running", process.name)
            process.run()
            process = self.scheduler.get_next_process()

    def shutdown(self):
        # Kill completed processes

        self.unassign_creeps()

    def unassign_creeps(self):
        pids = self.scheduler.list_pids()

        for name in Object.keys(Game.creeps):
            creep = Game.creeps[name]
            if not creep.assigned:
                continue

            if not pids.includes(str(creep.assigned)):
                creep.unassign()

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

    def check_version(self):
        if Memory.os.VERSION != js_global.VERSION:
            Memory.os.VERSION = js_global.VERSION
            return True

        return False

    def validate_memory(self):
        if _.isUndefined(Memory.os):
            Memory.os = {}

        if _.isUndefined(Memory.os.VERSION):
            Memory.os.VERSION = -1

        if _.isUndefined(Memory.os.kernel):
            Memory.os.kernel = {}

        if _.isUndefined(Memory.stats):
            Memory.stats = {}

        if _.isUndefined(Memory.stats.cpu):
            Memory.stats.cpu = {}

        self.memory = Memory.os.kernel
