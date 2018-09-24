
from defs import *
# he's at 465k into rcl5 i'm at 161k into rcl 4
# 102k into rcl 5 i'm at 388k into rcl 4
js_global.USERNAME = 'Lisp'
js_global.VERSION = 1226
js_global.CONTROLLER_SIGN = 'Placeholder till I think of something cool'

js_global.CREEP_SAY = False

js_global.BUILD_ORDER = [STRUCTURE_SPAWN, STRUCTURE_TOWER, STRUCTURE_EXTENSION, STRUCTURE_STORAGE,
                         STRUCTURE_TERMINAL, STRUCTURE_LINK, STRUCTURE_CONTAINER,
                         STRUCTURE_EXTRACTOR, STRUCTURE_ROAD, STRUCTURE_LAB]
js_global.WALL_WIDTH = {6: 1, 7: 3, 8: 10}
js_global.ROAD_RCL = 4

js_global.MIN_REPAIR = 0.7
js_global.TOWER_REPAIR = 0.5

js_global.MAX_DEATH_TIMER = 300

js_global.STORAGE_MIN = {4: 20000, 5: 50000, 6: 50000, 7: 50000, 8: 50000}
js_global.STORAGE_MAX = {4: 50000, 5: 200000, 6: 200000, 7: 200000, 8: 200000}

js_global.MIN_RESERVE_TICKS = 2500

js_global.TOWER_MIN = 0.8

js_global.BODY_ORDER = [TOUGH, ATTACK, RANGED_ATTACK, WORK, CARRY, MOVE, HEAL]
