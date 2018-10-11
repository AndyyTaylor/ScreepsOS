
from defs import *  # noqa
from base import base

__pragma__('noalias', 'keys')
__pragma__('noalias', 'name')


Object.defineProperties(Room.prototype, {
    'creeps': {
        'get': lambda: this._get_creeps()
    }, 'center': {
        'get': lambda: this._get_center()
    }, 'cent_link': {
        'get': lambda: this._get_cent_link()
    }, 'flags': {
        'get': lambda: this.find(FIND_FLAGS)
    }, 'feed_locations': {
        'get': lambda: this._get_feed_locations()
    }, 'construction_sites': {
        'get': lambda: this.find(FIND_MY_CONSTRUCTION_SITES)
    }, 'hostile_military': {
        'get': lambda: this._get_hostile_military()
    }, 'spawns': {
        'get': lambda: _.filter(this.find(FIND_STRUCTURES),
                                lambda s: s.structureType == STRUCTURE_SPAWN)
    }, 'terminal': {
        'get': lambda: _.filter(this.find(FIND_STRUCTURES),
                                lambda s: s.structureType == STRUCTURE_TERMINAL)[0]
    }, 'mineral': {
        'get': lambda: this.find(FIND_MINERALS)[0]
    }, 'repair_sites': {
        'get': lambda: _.filter(this.find(FIND_STRUCTURES),
                                lambda s: s.structureType != STRUCTURE_WALL and
                                         s.structureType != STRUCTURE_RAMPART and
                                          s.hits < s.hitsMax * js_global.MIN_REPAIR)  # noqa
    }, 'dropped_energy': {
        'get': lambda: _.filter(this.find(FIND_DROPPED_RESOURCES),
                                lambda r: r.resourceType == RESOURCE_ENERGY)
    }, 'towers': {
        'get': lambda: _.filter(this.find(FIND_STRUCTURES),
                                lambda s: s.structureType == STRUCTURE_TOWER)
    }, 'rcl': {
        'get': lambda: 0 if _.isUndefined(this.controller) else this.controller.level
    }, 'tombstones': {
        'get': lambda: this.find(FIND_TOMBSTONES)
    }, 'sources': {
        'get': lambda: this.find(FIND_SOURCES)
    }, 'structures': {
        'get': lambda: this.find(FIND_STRUCTURES)
    }, 'walls': {
        'get': lambda: this._get_walls()
    }, 'damaged_walls': {
        'get': lambda: this._get_damaged_walls()
    }
})


def _get_center():
    if not _.isUndefined(this.storage):
        return this.storage.pos
    elif not _.isUndefined(Game.flags[this.name]):
        pos = Game.flags[this.name].pos

        return __new__(RoomPosition(pos.x + 5, pos.y + 5, this.name))
    else:
        return __new__(RoomPosition(25, 25, this.name))


def _get_hostile_military():
    if _.isUndefined(this._hostile_military):
        whitelist = JSON.parse(RawMemory.foreignSegment.data).int_max
        whitelist.remove('Lisp')

        this._hostile_military = _.filter(this.find(FIND_CREEPS),
                                          lambda c:
                                          c.getActiveBodyparts(ATTACK) +
                                          c.getActiveBodyparts(RANGED_ATTACK) +
                                          c.getActiveBodyparts(HEAL) +
                                          c.getActiveBodyparts(WORK) > 0 and
                                          (not c.my or c.memory.red_team) and
                                          not whitelist.includes(c.owner.username))

    return this._hostile_military


def _get_feed_locations():
    if _.isUndefined(this._feed_locations):
        this._feed_locations = _.filter(this.structures,
                                        lambda s:
                                            s.structureType == STRUCTURE_SPAWN or
                                            s.structureType == STRUCTURE_EXTENSION or
                                            (s.structureType == STRUCTURE_TOWER and
                                             s.energy < s.energyCapacity * js_global.TOWER_MIN))

    return this._feed_locations


def _get_walls():
    if _.isUndefined(this._walls):
        this._walls = _.filter(this.structures,
                               lambda s: s.structureType == STRUCTURE_WALL or
                                         s.structureType == STRUCTURE_RAMPART)  # noqa

    return this._walls


def _get_damaged_walls():
    if _.isUndefined(this._damaged_walls):
        ideal_hits = this.memory.walls.hits
        this._damaged_walls = _.filter(this.walls, lambda w: w.hits < ideal_hits - js_global.MAX_WALL_DECAY)

    return this._damaged_walls


def _get_creeps():
    if _.isUndefined(this._creeps):
        name = this.name
        this._creeps = _.filter(Object.keys(Game.creeps),
                                lambda c: Game.creeps[c].memory.city == name)

    return this._creeps


def _get_sources():
    return this.find(FIND_SOURCES)


def _is_city():
    return not _.isUndefined(this.controller) and not _.isUndefined(this.controller.owner) \
        and this.controller.owner.username == js_global.USERNAME


def _is_remote():
    return not _.isUndefined(this.controller) and not _.isUndefined(this.controller.reservation) \
        and this.controller.reservation.username == js_global.USERNAME


def _is_full():
    spawns_full = this.energyAvailable == this.energyCapacityAvailable
    towers_full = True
    for tower in this.towers:
        if tower.energy < tower.energyCapacity * js_global.TOWER_MIN:
            towers_full = False
            break

    return spawns_full and towers_full


def _get_spawn_energy():
    creeps = this.find(FIND_MY_CREEPS)
    has_miner = False  # This will have to change when under seige
    has_hauler = False

    for creep in creeps:
        if creep.getActiveBodyparts(WORK) > 0 and creep.getActiveBodyparts(CARRY) < 3:
            has_miner = True
        elif not has_hauler and creep.getActiveBodyparts(CARRY) > 0 and \
                creep.getActiveBodyparts(WORK) < 1:
            has_hauler = True

            if not _.isUndefined(creep.room.storage):
                spos = creep.room.storage.pos
                if creep.pos.x == spos.x + 1 and creep.pos.y == spos.y + 1:
                    has_hauler = False

    if not _.isUndefined(this.storage):
        if this.storage.store[RESOURCE_ENERGY] > js_global.STORAGE_MIN[this.rcl]:
            has_miner = True

    if not has_hauler or not has_miner:
        return 300

    return this.energyCapacityAvailable


def _total_dropped_energy():
    total = 0
    for energy in this.dropped_energy:
        total += energy.amount

    return total


def _get_additional_workers():
    if _.isUndefined(this.memory.dropped_energy):
        this.memory.dropped_energy = this.total_dropped_energy()
        this.memory.dropped_energy_tick = Game.time
        this.memory.additional_workers = 0

        return 0

    if Game.time > this.memory.dropped_energy_tick + 750:
        this.memory.dropped_energy = this.total_dropped_energy()
        this.memory.dropped_energy_tick = Game.time

        if not _.isUndefined(this.storage):
            stored = this.storage.store[RESOURCE_ENERGY]
            avg = (js_global.STORAGE_MAX[this.rcl] + js_global.STORAGE_MIN[this.rcl]) / 2

            if stored > js_global.STORAGE_MAX[this.rcl]:
                this.memory.additional_workers += 1
            elif stored < avg:
                this.memory.additional_workers -= 1
        else:
            if this.total_dropped_energy() > 1000:
                this.memory.additional_workers += 1
            elif this.total_dropped_energy() < 200:
                this.memory.additional_workers -= 1

        this.memory.additional_workers = max(0, this.memory.additional_workers)
        this.memory.additional_workers = min(7, this.memory.additional_workers)

    return this.memory.additional_workers


def _get_cent_link():
    flag = Game.flags[this.name]
    link_x = flag.pos.x + base['central_link']['x']
    link_y = flag.pos.y + base['central_link']['y']

    structures = this.lookForAt(LOOK_STRUCTURES, link_x, link_y)
    for struct in structures:
        if struct.structureType == STRUCTURE_LINK:
            return Game.getObjectById(struct.id)

    # return undefined


def _basic_matrix(ignore_creeps=False):  # Should pass in actual room name
    costs = __new__(PathFinder.CostMatrix)

    structures = this.find(FIND_STRUCTURES)
    for struct in structures:
        if struct.structureType != STRUCTURE_CONTAINER and \
                struct.structureType != STRUCTURE_ROAD and \
                (struct.structureType != STRUCTURE_RAMPART or not struct.my):
            costs.set(struct.pos.x, struct.pos.y, 0xff)
        elif struct.structureType == STRUCTURE_ROAD:
            costs.set(struct.pos.x, struct.pos.y, 1)

    if not ignore_creeps:
        for creep in this.find(FIND_CREEPS):
            costs.set(creep.pos.x, creep.pos.y, 0xff)

    return costs


def _can_place_wall():
    freq = this.memory.walls.last_placed + js_global.WALL_PLACEMENT_FREQUENCY < Game.time
    hits = True
    for wall in this.walls:
        if wall.hits < this.memory.walls.hits - js_global.MAX_WALL_DECAY:
            hits = False
            break

    if not _.isUndefined(this.storage) and this.storage.store[RESOURCE_ENERGY] > js_global.STORAGE_MIN[this.rcl]:
        storage = True
    else:
        storage = False

    return freq and hits and storage


Room.prototype.get_sources = _get_sources
Room.prototype.is_city = _is_city
Room.prototype.is_remote = _is_remote
Room.prototype.is_full = _is_full
Room.prototype.get_spawn_energy = _get_spawn_energy
Room.prototype.total_dropped_energy = _total_dropped_energy
Room.prototype.get_additional_workers = _get_additional_workers
Room.prototype._get_feed_locations = _get_feed_locations
Room.prototype._get_hostile_military = _get_hostile_military
Room.prototype._get_walls = _get_walls
Room.prototype.basic_matrix = _basic_matrix
Room.prototype._get_creeps = _get_creeps
Room.prototype._get_center = _get_center
Room.prototype._get_cent_link = _get_cent_link
Room.prototype.can_place_wall = _can_place_wall
Room.prototype._get_damaged_walls = _get_damaged_walls
