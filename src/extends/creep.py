
from defs import *  # noqa

from tasks import *  # noqa


Object.defineProperties(Creep.prototype, {
    'assigned': {
        'get': lambda: this.memory.assigned
    },
})


def _assign(pid):
    this.memory.assigned = pid
    this.clear_task()


def _unassign():
    this.memory.assigned = None
    this.clear_task()


def _set_task(name, data={}):
    this.memory.task_name = name
    this.memory.task_data = data


def _clear_task():
    this.memory.task_name = None
    this.memory.task_data = None


def _is_idle():
    return _.isUndefined(this.memory.task_name) or not this.memory.task_name


def _get_task_instance(name, data={}):
    classes_by_name = {
        'harvest': Harvest,
        'gather': Gather,
        'upgrade': Upgrade,
        'travel': Travel,
        'feed': Feed,
        'build': Build
    }

    TaskClass = classes_by_name[name]

    return TaskClass(data)


def _run_current_task():
    if this.memory.task_name:
        task = _get_task_instance(this.memory.task_name, this.memory.task_data)
        task.run(this)


def _is_empty():
    return _.sum(this.carry) == 0


def _is_full():
    return _.sum(this.carry) == this.carryCapacity


Creep.prototype.assign = _assign
Creep.prototype.unassign = _unassign
Creep.prototype.set_task = _set_task
Creep.prototype.run_current_task = _run_current_task
Creep.prototype.is_empty = _is_empty
Creep.prototype.is_full = _is_full
Creep.prototype.is_idle = _is_idle
Creep.prototype.clear_task = _clear_task
