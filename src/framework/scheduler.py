
from defs import *  # noqa
from typing import List, Optional, Dict
from processes import *  # noqa
from framework.process import Process

__pragma__('noalias', 'undefined')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


process_classes = {
    'city': City,
    'minesite': MineSite,
    'roomplanner': RoomPlanner,
    'upgradesite': UpgradeSite,
    'feedsite': FeedSite,
    'buildsite': BuildSite,
    'spawning': Spawning,
    'repairsite': RepairSite,
    'defence': Defence,
    'logistics': Logistics,
    'management': Management,
    'remote': Remote,
    'remotemine': RemoteMine,
    'reserve': Reserve,
    'remotehaul': RemoteHaul,
    'claim': Claim,
    'remotework': RemoteWork,
    'simpleattack': SimpleAttack,
    'sappattack': SappAttack,
    'mineralsite': MineralSite,
    'wallrepair': WallRepair,
    'remoteinvaderdefence': RemoteInvaderDefence,
    'dismantle': Dismantle,
    'empire': Empire,
    'attackplanner': AttackPlanner
}


class Scheduler:

    def __init__(self):
        self.validate_memory()

        self.current_priority: int = 0
        self.current_index: int = 0
        self.processes: Dict[str, Process] = None
        self.queue: Dict[str, List[int]] = None

    def load_processes(self):
        self.processes = Object.assign({}, self.memory.processes)
        self.queue = Object.assign({}, self.memory.queue)

    def get_next_process(self) -> Optional[Process]:
        # Object keys should always be strings for consistency
        priorities: List[str] = Object.keys(self.queue)

        while not priorities.includes(str(self.current_priority)) and self.current_priority < 10:
            self.current_priority += 1
            self.current_index = 0

        if self.current_priority >= 10:
            return None

        pids: List[int] = list(self.queue[self.current_priority])
        pid: int = pids[self.current_index]

        self.current_index += 1
        if self.current_index >= len(pids):
            self.current_priority += 1
            self.current_index = 0

        if _.isUndefined(self.processes[str(pid)]):
            self.delete_process(pid)
            return self.get_next_process()

        return self.create_process(pid)

    def queue_processes(self):
        self.current_priority = 0  # shift_processes instead?
        self.current_index = 0

    def launch_process(self, name, data=None):
        pid = self.gen_pid()
        priority = process_classes[name](-1).priority

        proc = {
            'name': name,
            'pid': pid,
            'data': data,
            'priority': priority
        }
        self.processes[pid] = proc

        if priority not in self.queue:
            self.queue[priority] = []
        self.queue[priority].append(pid)

        self._grouped_by_name = undefined

    def shutdown(self):
        for pid in Object.keys(self.processes):
            if self.create_process(pid).is_completed():
                self.delete_process(pid)

        self.save_processes()

    def get_priority_of(self, pid):
        proc = self.processes[pid]

        return proc['priority']

    def delete_process(self, pid):
        proc = self.processes[str(pid)]

        if not _.isUndefined(proc):
            index = self.queue[proc['priority']].indexOf(int(pid))

            del self.processes[str(pid)]
            self.queue[str(proc['priority'])].splice(index, 1)

        self._grouped_by_name = undefined

    def create_process(self, pid):
        proc = self.processes[str(pid)]

        ProcessClass = process_classes[proc['name']]

        return ProcessClass(proc['pid'], proc['data'])

    def group_processes_by_name(self):
        if _.isUndefined(self._grouped_by_name):
            all_processes = Object.values(self.processes)
            self._grouped_by_name = dict(_.groupBy(all_processes, 'name'))

    def count_by_name(self, name, parent=None):
        self.group_processes_by_name()

        procs = self._grouped_by_name.get(name, [])

        if parent is not None:
            procs = _.filter(procs, lambda p: p.data.parent == parent)

        return len(procs)

    def proc_by_name(self, name, parent=None):
        self.group_processes_by_name()

        procs = self._grouped_by_name.get(name, [])

        if parent is not None:
            procs = _.filter(procs, lambda p: p.data.parent == parent)

        return procs

    def list_pids(self):
        return Object.keys(self.processes)

    def save_processes(self):
        self.memory.processes = self.processes
        self.memory.queue = self.queue

    def kill_all_processes(self):
        self.memory.processes = {}
        self.memory.queue = {}

    def validate_memory(self):
        if _.isUndefined(Memory.os.scheduler):
            Memory.os.scheduler = {}

        if _.isUndefined(Memory.os.scheduler.processes):
            Memory.os.scheduler.processes = {}

        if _.isUndefined(Memory.os.scheduler.queue):
            Memory.os.scheduler.queue = {}

        if _.isUndefined(Memory.os.scheduler.current_pid):
            Memory.os.scheduler.current_pid = 0

        self.memory = Memory.os.scheduler

    def gen_pid(self):
        self.memory.current_pid += 1
        return self.memory.current_pid
