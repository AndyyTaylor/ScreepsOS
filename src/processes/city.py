
from defs import *  # noqa

from framework.process import Process

__pragma__('noalias', 'keys')


class City(Process):

    def __init__(self, pid, data={}):
        super().__init__("city", pid, 5, data)

    def run(self):
        scheduler = js_global.kernel.scheduler

        for p in scheduler.proc_by_name('minesite'):
            print(Object.keys(p))

        if scheduler.count_by_name('minesite') < 1:
            scheduler.launch_process('minesite')
