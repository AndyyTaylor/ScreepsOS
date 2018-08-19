
from defs import *  # noqa

from framework.task import Task


class Upgrade(Task):

    def __init__(self, data={}):
        super().__init__('upgrade', data)

    def run(self, creep):
        controller = creep.room.controller
        if creep.pos.getRangeTo(controller) > 3:
            creep.moveTo(controller)
        else:
            creep.upgradeController(controller)
