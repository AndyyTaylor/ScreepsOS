
from defs import *  # noqa

from framework.task import Task


class Sign(Task):

    def __init__(self, data={}):
        super().__init__('sign', data)

    def _run(self, creep):
        creep.say('sign')
        controller = creep.room.controller
        if not creep.pos.isNearTo(controller):
            creep.moveTo(controller)
        else:
            creep.signController(controller, js_global.CONTROLLER_SIGN)

    def is_completed(self, creep):
        controller = creep.room.controller
        return not _.isUndefined(controller.sign) and controller.sign.text == js_global.CONTROLLER_SIGN
