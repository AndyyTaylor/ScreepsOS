
from defs import *  # noqa

from framework.scheduler import Scheduler, process_classes
from framework.ticketer import Ticketer

__pragma__('noalias', 'keys')


class Kernel():

    def __init__(self):
        self.new_upload = self.check_version()
        Memory.os.kernel.finished = False

        self.validate_memory()

        self.scheduler = Scheduler()

        if self.new_upload:
            print("-------------------------")
            print("NEW UPLOAD DETECTED -", js_global.VERSION)
            print("-------------------------")
            self.scheduler.kill_all_processes()
            self.unassign_creeps()

    def start(self):
        if _.isUndefined(self.ticketer):
            self.ticketer = Ticketer()  # Has to be declared after kernel finishes init

        self.last_cpu = 0

        self.launch_cities()  # Launch Empire

        self.scheduler.queue_processes()
        self.ticketer.load_tickets()

        # if len(self.ticketer.get_tickets_by_type("spawn")) < 1:
        #     self.ticketer.add_ticket("spawn", 'kernel')

        if self.new_upload:
            self.ticketer.clear_all_tickets()

            self.new_upload = False

        Memory.stats.cpu.start = self.get_cpu_diff()

    def run(self):
        process = self.scheduler.get_next_process()

        while process is not None:
            process.run()
            process = self.scheduler.get_next_process()

        Memory.stats.cpu.run = self.get_cpu_diff()

    def shutdown(self):
        self.scheduler.shutdown()
        self.ticketer.save_tickets()

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
                for i in range(room.controller.level - 1):
                    rcl_progress += CONTROLLER_LEVELS[i + 1]

                for i in range(7):
                    rcl_progressTotal += CONTROLLER_LEVELS[i + 1]

        Memory.stats.rcl = rcl_progress / rcl_progressTotal

        # build_tickets = self.ticketer.get_tickets_by_type("build")
        # print(len(build_tickets), '-', len(_.filter(build_tickets,
        #                                             lambda s: not s['completed'])),
        #       'build tickets')

        Memory.stats.cpu.shutdown = self.get_cpu_diff()
        Memory.stats.cpu.bucket = Game.cpu.bucket

        Memory.os.kernel.finished = True

    def unassign_creeps(self):
        pids = self.scheduler.list_pids()

        for name in Object.keys(Game.creeps):
            creep = Game.creeps[name]

            if not creep.assigned:
                if creep.memory.death_timer:
                    creep.memory.death_timer -= 1
                    creep.say(creep.memory.death_timer)
                else:
                    creep.memory.death_timer = js_global.MAX_DEATH_TIMER

                if creep.memory.death_timer <= 0:
                    creep.suicide()

                continue
            else:
                del creep.memory.death_timer

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
        if Memory.os.VERSION != js_global.VERSION or not Memory.os.kernel.finished:
            Memory.os.VERSION = js_global.VERSION
            return True

        return False

    def get_cpu_diff(self):
        diff = Game.cpu.getUsed() - self.last_cpu
        self.last_cpu = Game.cpu.getUsed()

        return diff

    def clear_memory(self):
        for name in Object.keys(Memory.creeps):
            if not Game.creeps[name] and (not Memory.creeps['created'] or
                                          Memory.creeps['created'] < Game.time - 100):
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

        if _.isUndefined(Memory.stats.tickets):
            Memory.stats.tickets = {}

        self.memory = Memory.os.kernel
