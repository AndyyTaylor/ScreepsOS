
from defs import *  # noqa

from framework.scheduler import Scheduler, process_classes

__pragma__('noalias', 'keys')


class Kernel():

    def __init__(self):
        self.validate_memory()

        self.scheduler = Scheduler()

        new_upload = self.check_version()
        if new_upload:
            self.scheduler.kill_all_processes()

    def start(self):
        self.last_cpu = 0

        self.launch_cities()  # Launch Empire

        self.scheduler.queue_processes()

        Memory.stats.cpu.start = self.get_cpu_diff()

    def run(self):
        process = self.scheduler.get_next_process()

        while process is not None:
            # print("Running", process.name)
            process.run()
            process = self.scheduler.get_next_process()

        Memory.stats.cpu.run = self.get_cpu_diff()

    def shutdown(self):
        self.scheduler.shutdown()

        self.unassign_creeps()
        self.clear_memory()

        for name in Object.keys(process_classes):
            num = self.scheduler.count_by_name(name)
            Memory.stats.processes.count[name] = num

        Memory.stats.gcl = Game.gcl.progress / Game.gcl.progressTotal

        rcl_progress = 0
        rcl_progressTotal = 0
        for name in Object.keys(Game.rooms):
            room = Game.rooms[name]
            if room.is_city():
                rcl_progress += room.controller.progress
                rcl_progressTotal += CONTROLLER_LEVELS[7]  # Check that this is cumulative

        Memory.stats.rcl = rcl_progress / rcl_progressTotal
        Memory.stats.cpu.shutdown = self.get_cpu_diff()
        Memory.stats.cpu.bucket = Game.cpu.bucket

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

    def get_cpu_diff(self):
        diff = Game.cpu.getUsed() - self.last_cpu
        self.last_cpu = Game.cpu.getUsed()

        return diff

    def clear_memory(self):
        for name in Object.keys(Memory.creeps):
            if not Game.creeps[name]:
                del Memory.creeps[name]

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

        if _.isUndefined(Memory.stats.processes):
            Memory.stats.processes = {}

        if _.isUndefined(Memory.stats.processes.count):
            Memory.stats.processes.count = {}

        self.memory = Memory.os.kernel
