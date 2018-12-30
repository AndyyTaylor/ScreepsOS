
from defs import *  # noqa
from typing import Any, Optional, List

from framework.scheduler import Scheduler
from framework.ticketer import Ticketer


class Process:
    def __init__(self, name: str, pid: int, priority: int, data=None) -> None:
        if data is None:
            data = {}

        self.name = name
        self._pid = pid
        self._data: Any = data

        self._killed = False

        self.priority = priority
        self.scheduler: Scheduler = js_global.kernel.scheduler
        self.ticketer: Ticketer = js_global.kernel.ticketer

        if _.isUndefined(self._data.build_tickets):
            self._data.build_tickets = []
        
        if _.isUndefined(self._data.sleep):
            self._data.sleep = None

    def run(self) -> None:
        if self._data.sleep is None or Game.time > self._data.sleep:
            self._run()

    def launch_child_process(self, name: str, data=None) -> None:
        data['parent'] = self._pid

        self.scheduler.launch_process(name, data)

    def is_completed(self) -> bool:
        if self._killed:
            return True

        return False

    def kill(self) -> None:
        self._killed = True

    def sleep(self, duration: int) -> None:
        """ Set process to sleep for duration in ticks """
        self._data.sleep = Game.time + duration
    
    def _run(self) -> None:
        """ Placeholder for child to override """
        pass
