
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
    }, 'dropped_energy': {
        'get': lambda: _.filter(this.find(FIND_DROPPED_RESOURCES),
                                lambda r: r.resourceType == RESOURCE_ENERGY)
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

    if Game.time > this.memory.dropped_energy_tick + 800:
        this.memory.dropped_energy = this.total_dropped_energy()
        this.memory.dropped_energy_tick = Game.time

        if this.total_dropped_energy() > 1000:
            this.memory.additional_workers += 1
        else:
            this.memory.additional_workers -= 1

        print(this.total_dropped_energy(), this.memory.additional_workers)
    return this.memory.additional_workers


Room.prototype.get_sources = _get_sources
Room.prototype.is_city = _is_city
Room.prototype.is_full = _is_full
Room.prototype.get_spawn_energy = _get_spawn_energy
Room.prototype.total_dropped_energy = _total_dropped_energy
Room.prototype.get_additional_workers = _get_additional_workers
