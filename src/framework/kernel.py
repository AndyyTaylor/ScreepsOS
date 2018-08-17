
from defs import *  # noqa

from framework.scheduler import Scheduler


class Kernel():

    def __init__(self):
        self.validate_memory()

        self.scheduler = Scheduler()

        new_upload = self.check_version()
        if new_upload:
            self.scheduler.kill_all_processes()

    def start(self):
        if self.scheduler.count_by_name('city') < 1:
            self.scheduler.launch_process('city')

        self.scheduler.queue_processes()

    def run(self):
        process = self.scheduler.get_next_process()

        while process is not None:
            process.run()
            print("Running", process.name)
            process = self.scheduler.get_next_process()

    def shutdown(self):
        pass

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

        self.memory = Memory.os.kernel
