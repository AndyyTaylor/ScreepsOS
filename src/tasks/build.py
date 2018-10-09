
from defs import *  # noqa

from framework.task import Task


class Build(Task):

    def __init__(self, data=None):
        super().__init__('build', data)

    def _run(self, creep):
        target = Game.getObjectById(self._data.site_id)
        if not target:
            self._data.completed = True
            return

        if not creep.pos.inRangeTo(target, 3):
            creep.moveTo(target)
        else:
            creep.build(target)

    def is_completed(self, creep):
        return creep.is_empty() or self._data.completed
