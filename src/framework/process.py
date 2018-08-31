
from defs import *  # noqa


class Process():

    def __init__(self, name, pid, priority, data={}):
        self.name = name
        self._pid = pid
        self._data = data

        self._killed = False

        self.priority = priority
        self.scheduler = js_global.kernel.scheduler
        self.ticketer = js_global.kernel.ticketer

        if _.isUndefined(self._data.build_tickets):
            self._data.build_tickets = []

    def run(self):
        # Check if process is sleeping

        self._run()

    def launch_child_process(self, name, data={}):
        data['parent'] = self._pid

        self.scheduler.launch_process(name, data)

    def is_completed(self):
        if self._killed:
            return True

        return False

    def kill(self):
        self._killed = True
