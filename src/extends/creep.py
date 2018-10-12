
from defs import *  # noqa

from tasks import *  # noqa

classes_by_name = {
    'harvest': Harvest,
    'gather': Gather,
    'upgrade': Upgrade,
    'travel': Travel,
    'feed': Feed,
    'build': Build,
    'repair': Repair,
    'withdraw': Withdraw,
    'deposit': Deposit,
    'sign': Sign
}

Object.defineProperties(Creep.prototype, {
    'assigned': {
        'get': lambda: this.memory.assigned
    },
})


def _drive_to(target, opts=None):
    if opts is None:
        opts = {}

    if _.isUndefined(this.memory.drive):
        this.memory.drive = {
            'update_at': Game.time,
            'path': None,
            'target_pos': None,
            'maxOps': 2000
        }

    if _.isUndefined(target.pos):
        target_pos = target
    else:
        target_pos = target.pos

    if this.memory.drive.update_at <= Game.time or this.memory.drive.target_pos['x'] != target_pos.x or \
            this.memory.drive.target_pos['y'] != target_pos.y:
        opts['roomCallback'] = Room.basic_callback
        # print("Updating path")
        if _.isUndefined(opts['range']):
            opts['range'] = 0

        opts['maxOps'] = this.memory.drive.maxOps
        results = PathFinder.search(this.pos, {'pos': target_pos, 'range': opts['range']}, opts)

        if results.incomplete:
            this.memory.drive.maxOps = min(js_global.MAX_OPS, this.memory.drive.maxOps + 500)
        else:
            this.memory.drive.maxOps = max(js_global.MIN_OPS, this.memory.drive.maxOps - 500)

        this.memory.drive.path = _store_path(results.path)
        this.memory.drive.target_pos = target_pos
        this.memory.drive.update_at = Game.time + 10 * this.memory.drive.maxOps / 1000
        # TODO Determine path cache invalidity better

    # this.say(this.moveByPath(_load_path(this.memory.drive.path)))
    this.room.visual.poly(_load_path(this.memory.drive.path))
    if this.moveByPath(_load_path(this.memory.drive.path)) == -5:
        this.memory.drive.update_at = Game.time


def _store_path(path):
    new_path = []
    for tile in path:
        new_path.append({'x': tile.x, 'y': tile.y, 'roomName': tile.roomName})

    return new_path


def _load_path(path):
    new_path = []
    for tile in path:
        new_path.append(__new__(RoomPosition(tile['x'], tile['y'], tile['roomName'])))

    return new_path


def _distToClosest(objects):
    closest = this.pos.findClosestByRange(objects)

    return this.pos.getRangeTo(closest)


def _assign(pid):
    this.memory.assigned = pid
    this.clear_task()


def _unassign():
    this.memory.assigned = None
    this.clear_task()


def _set_task(name, data=None):
    this.memory.task_name = name
    this.memory.task_data = data


def _clear_task():
    this.memory.task_name = None
    this.memory.task_data = None


def _is_idle():
    is_idle = _.isUndefined(this.memory.task_name) or not this.memory.task_name

    return is_idle


def _get_task_instance(name, data=None):
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


Creep.prototype.distToClosest = _distToClosest
Creep.prototype.assign = _assign
Creep.prototype.unassign = _unassign
Creep.prototype.set_task = _set_task
Creep.prototype.run_current_task = _run_current_task
Creep.prototype.is_empty = _is_empty
Creep.prototype.is_full = _is_full
Creep.prototype.is_idle = _is_idle
Creep.prototype.clear_task = _clear_task
Creep.prototype.drive_to = _drive_to
