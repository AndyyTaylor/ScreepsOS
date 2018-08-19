
from defs import *  # noqa


Object.defineProperties(Room.prototype, {
    'flags': {
        'get': lambda: this.find(FIND_FLAGS)
    },
})


def _get_sources():
    return this.find(FIND_SOURCES)


def _is_city():
    return not _.isUndefined(this.controller) and not _.isUndefined(this.controller.owner) \
        and this.controller.owner.username == js_global.USERNAME


Room.prototype.get_sources = _get_sources
Room.prototype.is_city = _is_city
