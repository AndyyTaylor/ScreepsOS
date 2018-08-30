
from defs import *  # noqa


Object.defineProperties(Room.prototype, {
    'flags': {
        'get': lambda: this.find(FIND_FLAGS)
    }, 'feed_locations': {
        'get': lambda: _.filter(this.find(FIND_STRUCTURES),
                                lambda s: s.structureType == STRUCTURE_SPAWN or
                                s.structureType == STRUCTURE_EXTENSION)
    }, 'construction_sites': {
        'get': lambda: this.find(FIND_CONSTRUCTION_SITES)
    }, 'spawns': {
        'get': lambda: _.filter(this.find(FIND_STRUCTURES),
                                lambda s: s.structureType == STRUCTURE_SPAWN)
    }, 'repair_sites': {
        'get': lambda: _.filter(this.find(FIND_STRUCTURES),
                                lambda s: s.structureType != STRUCTURE_WALL and
                                         s.structureType != STRUCTURE_RAMPART and
                                          s.hits < s.hitsMax * js_global.MIN_REPAIR)  # noqa
    }
})


def _get_sources():
    return this.find(FIND_SOURCES)


def _is_city():
    return not _.isUndefined(this.controller) and not _.isUndefined(this.controller.owner) \
        and this.controller.owner.username == js_global.USERNAME


def _is_full():
    return this.energyAvailable == this.energyCapacityAvailable


def _get_spawn_energy():
    if len(this.find(FIND_MY_CREEPS)) < 6:
        return 300

    return this.energyCapacityAvailable


Room.prototype.get_sources = _get_sources
Room.prototype.is_city = _is_city
Room.prototype.is_full = _is_full
Room.prototype.get_spawn_energy = _get_spawn_energy
