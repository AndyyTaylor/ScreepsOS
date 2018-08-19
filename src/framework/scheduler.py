
from defs import *  # noqa
from processes import *  # noqa

__pragma__('noalias', 'undefined')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')

process_classes = {
    'city': City,
    'minesite': MineSite,
    'roomplanner': RoomPlanner
}


class Scheduler():

    def __init__(self):
        self.validate_memory()

        self.processes = Object.assign({}, self.memory.processes)
        self.queue = Object.assign({}, self.memory.queue)
        self.completed = []

    def get_next_process(self):
        if self.current_priority >= len(Object.keys(self.processes)):
            return None

        proc = self.processes[Object.keys(self.processes)[self.current_priority]]
        self.current_priority += 1
        ProcessClass = process_classes[proc['name']]

        return ProcessClass(proc['pid'], proc['data'])

    def queue_processes(self):
        self.current_priority = 0  # shift_processes instead?

    def launch_process(self, name, data={}):
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
        self.queue[priority] += pid

        self._grouped_by_name = undefined

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
        pass

    def kill_all_processes(self):
        pass

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
