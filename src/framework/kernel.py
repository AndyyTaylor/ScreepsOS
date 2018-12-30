
from defs import *  # noqa
from typing import Dict, Any
from math import ceil

from framework.scheduler import Scheduler, process_classes
from framework.ticketer import Ticketer
# from framework.process import Process

__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')


class Kernel:

    def __init__(self) -> None:
        self.validate_memory()

        self.last_cpu: float = 0.0
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
        self.validate_memory()  # Doing this again means memory can be wiped without heap reset

        Memory.os.kernel.finished = False

        if self.ticketer is None:
            self.ticketer = Ticketer()  # Has to be declared after kernel finishes init

        self.last_cpu = 0
        self.process_cpu = {}

        self.launch_empire()  # Launch Empire

        self.scheduler.load_processes()
        self.scheduler.queue_processes()
        self.ticketer.load_tickets()

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
        self.log_rooms()
        self.log_resources()

        Memory.stats.tickets = {}
        Memory.stats.tickets.count = {
            'spawn': len(self.ticketer.get_tickets_by_type('spawn')),
            'build': len(self.ticketer.get_tickets_by_type('build'))
        }

        Memory.stats.relations = {}
        Memory.stats.relations.disliked = {
            'Joe': {
                'score': -100,
                'reason': 'attacked me'
            }, 'Hurimi': {
                'score': -10,
                'reason': 'TooAngel user'
            }
        }

        Memory.stats.credits = Game.market.credits
        Memory.stats.cpu.shutdown = self.get_cpu_diff()
        Memory.stats.cpu.bucket = Game.cpu.bucket
        Memory.stats.memory = {'size': len(RawMemory.get())}

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

    def log_processes(self) -> None:
        Memory.stats.processes.cpu = self.process_cpu

        for name in Object.keys(process_classes):
            num = self.scheduler.count_by_name(name)
            Memory.stats.processes.count[name] = num

    def get_cpu_diff(self):
        diff = Game.cpu.getUsed() - self.last_cpu
        self.last_cpu = Game.cpu.getUsed()

        return diff

    def log_rooms(self):
        if _.isUndefined(Memory.stats.rooms):
            Memory.stats.rooms = {}

        for name in Object.keys(Game.rooms):
            room = Game.rooms[name]
            stats = Memory.stats.rooms[name] or {}

            if room.is_city() or room.is_remote():
                if not _.isUndefined(Memory.stats.rooms[name]) and not _.isUndefined(Memory.stats.rooms[name].expenses):
                    expenses = Object.assign({'build': 0, 'repair': 0, 'upgrade': 0, 'decay': 0}, Memory.stats.rooms[name].expenses)
                else:
                    expenses = {'build': 0, 'repair': 0, 'upgrade': 0, 'decay': 0}
                income = {'local_harvest': 0, 'remote_harvest': 0}
                events = room.getEventLog()
                for event in events:
                    if event.event == EVENT_BUILD:
                        expenses['build'] += event.data.energySpent
                    elif event.event == EVENT_REPAIR:
                        expenses['repair'] += event.data.energySpent
                    elif event.event == EVENT_UPGRADE_CONTROLLER:
                        expenses['upgrade'] += event.data.energySpent
                    elif event.event == EVENT_HARVEST:
                        if room.is_city():
                            if not _.isUndefined(Memory.stats.rooms[name].lharvest):
                                Memory.stats.rooms[name].lharvest.harvest += event.data.amount
                            income['local_harvest'] += event.data.amount
                        else:
                            income['remote_harvest'] += event.data.amount

                for resource in room.find(FIND_DROPPED_RESOURCES):
                    expenses['decay'] += ceil(resource.amount / 1000)

                stats.expenses = expenses
                stats.income = income

            if room.is_city():
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
                    if _.isUndefined(store.store):
                        resources[RESOURCE_ENERGY] += store.energy
                    else:
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

                total = 0
                count = max(len(room.walls), 1)
                for wall in room.walls:
                    total += wall.hits
                avg = total / count
                stats.walls = {
                    'total': total,
                    'avg': avg,
                    'count': count
                }

                stats.additionalWorkers = room.get_additional_workers()  # Room rcl 1 9528657

                # room.memory.towers.attack = 0
                # room.memory.towers.heal = 0
                # room.memory.towers.repair = 0

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
        expenditure = Memory.stats.expenditure or {}
        gincome = Memory.stats.income or {}

        for name in Object.keys(Memory.stats.rooms):
            if _.isUndefined(Game.rooms[name]):
                continue

            if Game.rooms[name].is_city():
                stored = Memory.stats.rooms[name].stored
                for resource in Object.keys(stored):
                    if resource in resources:
                        resources[resource] += stored[resource]
                    else:
                        resources[resource] = stored[resource]

            if Game.rooms[name].is_city() or Game.rooms[name].is_remote():
                expenses = Memory.stats.rooms[name].expenses
                for expense in Object.keys(expenses):
                    if expense in expenditure:
                        expenditure[expense] += expenses[expense]
                    else:
                        expenditure[expense] = expenses[expense]

                    Memory.stats.rooms[name].expenses[expense] = 0

                lincome = Memory.stats.rooms[name].income
                for income in Object.keys(lincome):
                    if income in gincome:
                        gincome[income] += lincome[income]
                    else:
                        gincome[income] = lincome[income]

                    Memory.stats.rooms[name].income[income] = 0

        Memory.stats.resources = resources
        Memory.stats.expenditure = expenditure
        Memory.stats.income = gincome

    def launch_empire(self):
        if self.scheduler.count_by_name('empire') < 1:
            self.scheduler.launch_process('empire')

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
