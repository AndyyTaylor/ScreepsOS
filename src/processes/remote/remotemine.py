
from defs import *  # noqa

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')
__pragma__('noalias', 'name')


class RemoteMine(CreepProcess):

    def __init__(self, pid, data=None):
        super().__init__('remotemine', pid, 5, data)

        if pid != -1:
            self.room = Game.rooms[self._data.room_name]
            self.mine_room = Game.rooms[self._data.mine_room]
            self.source = Game.getObjectById(self._data.source_id)

    def _run(self):
        if _.isUndefined(self._data.has_init):
            self.init()

        self.run_creeps()

    def run_creep(self, creep):
        self.source = Game.getObjectById(self._data.source_id)

        if self._data.creep_names.indexOf(creep.js_name) == 0 and (not _.isNull(self.source) and self.source.energy > 0):  # noqa
            self.move_to_drop(creep)

        if _.isNull(self.source):
            creep.moveTo(__new__(RoomPosition(25, 25, self._data.mine_room)))
        else:
            if creep.pos.isNearTo(self.source) or creep.pos.getRangeTo(self.source) < self.source.ticksToRegeneration:
                if self.source.energy > 0:
                    Memory.stats.rooms[self._data.room_name].rharvest.harvest += min(self.source.energy,
                                                                                     creep.getActiveBodyparts(WORK) * 2)
                    creep.harvest(self.source)
                elif creep.carry.energy > 0:
                    site = creep.pos.findClosestByRange(creep.room.construction_sites)
                    if not _.isNull(site):
                        if creep.pos.inRangeTo(site, 3):
                            creep.build(site)
                        else:
                            creep.moveTo(site)
                    else:
                        struct = creep.pos.findClosestByRange(_.filter(creep.room.structures,
                                                                       lambda s: s.hits < s.hitsMax))
                        if not _.isNull(struct):
                            if creep.pos.inRangeTo(struct, 3):
                                creep.repair(struct)
                            else:
                                creep.moveTo(struct)
                if creep.carry.energy < creep.carryCapacity:
                    resource = creep.pos.findClosestByRange(creep.room.find(FIND_DROPPED_RESOURCES))
                    if not _.isNull(resource) and creep.pos.isNearTo(resource):
                        creep.pickup(resource)
                        creep.say('resource')
                    else:
                        cont = Game.getObjectById(self._data.deposit_id)
                        creep.say(cont)
                        if not _.isNull(cont):
                            creep.set_task('withdraw', {'target_id': cont.id})
                        else:
                            creep.moveTo(self.source)
            else:
                creep.moveTo(self.source)

        creep.run_current_task()

    def move_to_drop(self, creep):
        if creep.pos.x == self._data.drop_x and creep.pos.y == self._data.drop_y:
            return

        is_empty = len(self.room.lookForAt(LOOK_CREEPS, self._data.drop_x, self._data.drop_y)) == 0
        if is_empty:
            creep.set_task('travel', {'dest_x': self._data.drop_x, 'dest_y': self._data.drop_y,
                                      'dest_room_name': self._data.mine_room})

    def _needs_creeps(self, creep_names):
        return len(creep_names) < 1

    def is_valid_creep(self, creep):
        return creep.memory.role == 'rminer'

    def gen_body(self, energyAvailable):
        body = [WORK, CARRY, MOVE]
        mod = [WORK, WORK, MOVE]
        total_work = 1

        while self.get_body_cost(body.concat(mod)) <= energyAvailable and total_work < 8:
            total_work += 2
            body = body.concat(mod)

        Memory.stats.rooms[self._data.room_name].rharvest.spawn += self.get_body_cost(body)

        return body, {'remote': True, 'role': 'rminer'}

    def init(self):
        self.mine_room = Game.rooms[self._data.mine_room]

        if _.isUndefined(Memory.stats.rooms[self._data.room_name].rharvest):
            Memory.stats.rooms[self._data.room_name].rharvest = {}

        if _.isUndefined(Memory.stats.rooms[self._data.room_name].rharvest.harvest):
            Memory.stats.rooms[self._data.room_name].rharvest.harvest = 0

        if _.isUndefined(Memory.stats.rooms[self._data.room_name].rharvest.spawn):
            Memory.stats.rooms[self._data.room_name].rharvest.spawn = 0

        if _.isUndefined(Memory.stats.rooms[self._data.room_name].rharvest.transfer):
            Memory.stats.rooms[self._data.room_name].rharvest.transfer = 0

        if _.isUndefined(self.mine_room):
            return

        drop_pos = self.load_terrain()
        drop_pos, deposit_id = self.load_deposit(drop_pos)

        if deposit_id is None:
            ticket = {
                'type': STRUCTURE_CONTAINER,
                'x': drop_pos.x,
                'y': drop_pos.y,
                'city': self._data.mine_room
            }
            tid = self.ticketer.add_ticket('build', self._pid, ticket)
            self._data.build_tickets.append(tid)

        self._data.drop_x = drop_pos.x
        self._data.drop_y = drop_pos.y
        self._data.deposit_id = deposit_id

        self._data.has_init = True

    def load_terrain(self):
        drop_pos = None
        pos = self.source.pos
        terrain = self.mine_room.lookForAtArea(LOOK_TERRAIN, pos.y - 1, pos.x - 1,
                                               pos.y + 1, pos.x + 1, True)
        structs = self.mine_room.lookForAtArea(LOOK_STRUCTURES, pos.y - 1, pos.x - 1,
                                               pos.y + 1, pos.x + 1)

        for tile in terrain:
            if tile.terrain != 'wall':
                walkable = True
                if not _.isUndefined(structs[tile.y][tile.x]):
                    for struct in structs[tile.y][tile.x]:
                        type = struct.structureType
                        if type != STRUCTURE_ROAD and type != STRUCTURE_CONTAINER:
                            walkable = False
                            break

                if walkable:
                    drop_pos = {'x': tile.x, 'y': tile.y}
                    break

        return drop_pos

    def load_deposit(self, drop_pos):
        deposit_id = None
        x, y = self.source.pos.x, self.source.pos.y
        nearby_structs = self.room.lookForAtArea(LOOK_STRUCTURES, y - 1, x - 1, y + 1, x + 1, True)
        for struct in nearby_structs:
            if struct.structureType == STRUCTURE_CONTAINER:
                deposit_id = struct.id
                break

        if deposit_id is not None:
            drop_pos = Game.getObjectById(deposit_id).pos

        return drop_pos, deposit_id
