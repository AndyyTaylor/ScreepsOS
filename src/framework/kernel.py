
from defs import *  # noqa
from typing import Dict, Any

from framework.scheduler import Scheduler, process_classes
from framework.ticketer import Ticketer
from framework.process import Process

__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')


class Kernel:

    def __init__(self) -> None:
        self.validate_memory()

        self.last_cpu: float = 0
        self.new_upload: bool = self.check_version()
        self.process_cpu: Dict[str, Dict[str, Any]] = {}
        self.scheduler: Scheduler = Scheduler()
        self.ticketer: Ticketer = None

        Memory.stats.resets += 1

        if len(RawMemory.get()) > js_global.MEMORY_MAX:
            print("MEMORY_MAX REACHED -> Resetting...")
            self.new_upload = True

        if self.new_upload:
            print("-------------------------")
            print("NEW UPLOAD DETECTED -", js_global.VERSION)
            print("-------------------------")
            self.scheduler.kill_all_processes()
            self.scheduler.load_processes()
            self.unassign_creeps()

    def start(self) -> None:
        Memory.os.kernel.finished = False

        if self.ticketer is None:
            self.ticketer = Ticketer()  # Has to be declared after kernel finishes init

        self.last_cpu = 0
        self.process_cpu = {}

        self.scheduler.load_processes()
        self.scheduler.queue_processes()
        self.ticketer.load_tickets()

        self.launch_cities()  # Launch Empire

        if self.new_upload:
            self.ticketer.clear_all_tickets()

            self.new_upload = False

        Memory.stats.cpu.start = self.get_cpu_diff()

    def run(self) -> None:
        process: Process = self.scheduler.get_next_process()

        while process is not None:
            if _.isUndefined(self.process_cpu[process.name]):
                self.process_cpu[process.name] = {'total': 0, 'count': 0, 'max': 0}

            start = Game.cpu.getUsed()
            process.run()
            end = Game.cpu.getUsed()

            diff = end - start
            self.process_cpu[process.name]['total'] += diff
            self.process_cpu[process.name]['count'] += 1
            self.process_cpu[process.name]['max'] = max(diff, self.process_cpu[process.name]['max'])
            self.process_cpu[process.name]['avg'] = self.process_cpu[process.name]['total'] / \
                self.process_cpu[process.name]['count']

            process: Process = self.scheduler.get_next_process()

        Memory.stats.cpu.run = self.get_cpu_diff()

    def shutdown(self) -> None:
        self.scheduler.shutdown()
        self.ticketer.save_tickets()

        self.unassign_creeps()
        self.clear_memory()

        self.log_defence()
        self.log_gcl()
        self.log_processes()
        self.log_rcl()
        self.log_resources()
        self.log_rooms()

        Memory.stats.tickets = {}
        Memory.stats.tickets.count = {
            'spawn': len(self.ticketer.get_tickets_by_type('spawn')),
            'build': len(self.ticketer.get_tickets_by_type('build'))
        }

        Memory.stats.credits = Game.market.credits
        Memory.stats.cpu.shutdown = self.get_cpu_diff()
        Memory.stats.cpu.bucket = Game.cpu.bucket
        Memory.stats.memory = {'size': len(RawMemory.get())}

        Memory.os.kernel.finished = True

    def launch_cities(self) -> None:
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

    def log_processes(self) -> None:
        Memory.stats.processes.cpu = self.process_cpu

        for name in Object.keys(process_classes):
            num = self.scheduler.count_by_name(name)
            Memory.stats.processes.count[name] = num

    def get_cpu_diff(self):
        diff = Game.cpu.getUsed() - self.last_cpu
        self.last_cpu = Game.cpu.getUsed()

        return diff

    @staticmethod
    def check_version():
        if Memory.os.VERSION != js_global.VERSION or not Memory.os.kernel.finished:
            Memory.os.VERSION = js_global.VERSION
            return True

        return False

    @staticmethod
    def clear_memory():
        for name in Object.keys(Memory.creeps):
            creep = Game.creeps[name]
            cmem = Memory.creeps[name]
            if not creep and (not cmem['created'] or not cmem['spawnTime'] or
                              cmem['created'] < Game.time - cmem['spawnTime']):
                del Memory.creeps[name]

    @staticmethod
    def log_defence():
        Memory.stats.defence = {
            'overall': 0,
            'safeMode': 0
        }

    @staticmethod
    def log_gcl():
        Memory.stats.gcl = {
            'level': Game.gcl.level,
            'progress': Game.gcl.progress,
            'progressTotal': Game.gcl.progressTotal,
            'percentage': Game.gcl.progress / Game.gcl.progressTotal
        }

    @staticmethod
    def log_rcl():
        rcl_progress = 0
        rcl_progress_total = 0
        for name in Object.keys(Game.rooms):
            room = Game.rooms[name]
            if room.is_city():
                rcl_progress += room.controller.progress
                for i in range(room.controller.level - 1):
                    rcl_progress += CONTROLLER_LEVELS[i + 1]

                for i in range(7):
                    rcl_progress_total += CONTROLLER_LEVELS[i + 1]

        Memory.stats.rcl = {
            'percentage': rcl_progress / rcl_progress_total,
            'progress': rcl_progress,
            'progressTotal': rcl_progress_total
        }

    @staticmethod
    def log_resources():
        resources = {}
        for name in Object.keys(Memory.stats.rooms):
            stored = Memory.stats.rooms[name].stored
            for resource in Object.keys(stored):
                if resource in resources:
                    resources[resource] += stored[resource]
                else:
                    resources[resource] = stored[resource]

        Memory.stats.resources = resources

    @staticmethod
    def log_rooms():
        Memory.stats.rooms = {}

        for name in Object.keys(Game.rooms):
            room = Game.rooms[name]

            if not room.is_city():
                continue

            stats = {}

            stats.rcl = {
                'level': room.controller.level,
                'progress': room.controller.progress,
                'progressTotal': room.controller.progressTotal
            }

            resources = {'energy': 0}
            stores = _.filter(room.find(FIND_STRUCTURES),
                              lambda s: s.structureType == STRUCTURE_CONTAINER or
                                        s.structureType == STRUCTURE_LINK or
                                        s.structureType == STRUCTURE_STORAGE)  # noqa

            for store in stores:
                if isinstance(store, StructureLink):
                    resources[RESOURCE_ENERGY] += store.energy
                elif isinstance(store, StructureContainer) or isinstance(store, StructureStorage):
                    for rtype in Object.keys(store.store):
                        if not Object.keys(resources).includes(rtype):
                            resources[rtype] = store.store[rtype]
                        else:
                            resources[rtype] += store.store[rtype]

            stats.stored = resources

            total_spawns = len(room.spawns)
            num_working = 0
            for spawn in room.spawns:
                if not _.isNull(spawn.spawning):
                    num_working += 1

            stats.spawning = {
                'totalSpawns': total_spawns,
                'numWorking': num_working,
                'percBusy': num_working / total_spawns,
                'isFull': 1 if room.is_full() else 0,
                'energyPerc': room.energyAvailable / room.energyCapacityAvailable,
                'waiting': 1 if room.is_full() and num_working < total_spawns else 0
            }

            energy = 0
            for tower in room.towers:
                energy += tower.energy

            stats.towers = {
                'energy': energy,
                'attack': room.memory.towers.attack,
                'heal': room.memory.towers.heal,
                'repair': room.memory.towers.repair
            }

            stats.additionalWorkers = room.get_additional_workers()

            Memory.stats.rooms[name] = stats

    @staticmethod
    def validate_memory():
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
