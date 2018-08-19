
from defs import *  # noqa


Object.defineProperties(Room.prototype, {
    'flags': {
        'get': lambda: this.find(FIND_FLAGS)
    },
    'feed_locations': {
        'get': lambda: _.filter(this.find(FIND_STRUCTURES),
                                lambda s: s.structureType == STRUCTURE_SPAWN or
                                s.structureType == STRUCTURE_EXTENSION)
    }
})


def _get_sources():
    return this.find(FIND_SOURCES)


def _is_city():
    return not _.isUndefined(this.controller) and not _.isUndefined(this.controller.owner) \
        and this.controller.owner.username == js_global.USERNAME


def _is_full():
    return this.energyAvailable == this.energyCapacityAvailable


Room.prototype.get_sources = _get_sources
Room.prototype.is_city = _is_city
Room.prototype.is_full = _is_full
