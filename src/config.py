
from defs import *
# he's at 465k into rcl5 i'm at 161k into rcl 4
# 102k into rcl 5 i'm at 388k into rcl 4
js_global.USERNAME = 'Lisp'
js_global.VERSION = 1884

js_global.CONTROLLER_SIGN = 'Territory of Lisp [' + str(js_global.VERSION) + ']'

js_global.CREEP_SAY = False

js_global.BUILD_ORDER = [STRUCTURE_SPAWN, STRUCTURE_TOWER, STRUCTURE_EXTENSION, STRUCTURE_STORAGE,
                         STRUCTURE_TERMINAL, STRUCTURE_LINK, STRUCTURE_CONTAINER,
                         STRUCTURE_EXTRACTOR, STRUCTURE_ROAD, STRUCTURE_LAB, STRUCTURE_RAMPART]
js_global.WALL_WIDTH = {5: 1, 6: 2, 7: 3, 8: 4}
js_global.MIN_WALL_HITS = 50000
js_global.WALL_PLACEMENT_FREQUENCY = 50
js_global.MAX_WALL_DECAY = 10000
js_global.WALL_REINFORCEMENT = 50000
js_global.ROAD_RCL = 4

js_global.MIN_REPAIR = 0.7
js_global.TOWER_REPAIR = 0.5

js_global.MAX_DEATH_TIMER = 500

js_global.STORAGE_MIN = {4: 20000, 5: 50000, 6: 50000, 7: 50000, 8: 50000}
js_global.STORAGE_MAX = {4: 50000, 5: 200000, 6: 200000, 7: 200000, 8: 200000}
js_global.RESOURCE_MAX_STORAGE = 10000
js_global.RESOURCE_MIN_TERMINAL = 5000
js_global.RESOURCE_MAX_TERMINAL = 10000
js_global.ENERGY_MAX_TERMINAL = 50000

js_global.MIN_RESERVE_TICKS = 2500

js_global.TOWER_MIN = 0.8

js_global.MEMORY_MAX = 1000000

js_global.SCOUT_FREQ = 5
js_global.INVADER_USERNAME = 'Invader'

js_global.BODY_ORDER = [TOUGH, ATTACK, WORK, RANGED_ATTACK, CARRY, HEAL, MOVE]

js_global.REMOTE_WORK_DIST = 10
