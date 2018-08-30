
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

    def run(self):
        # Check if process is sleeping

        self._run()

    def launch_child_process(self, name, data={}):
        data['parent'] = self._pid

        self.scheduler.launch_process(name, data)

    def is_completed(self):
        if self._killed:
            return True

    def kill(self):
        self._killed = True
