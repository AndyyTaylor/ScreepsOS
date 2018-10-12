
from defs import *  # noqa

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')
__pragma__('noalias', 'name')


class SappAttack(CreepProcess):

    def __init__(self, pid, data=None):
        super().__init__('sappattack', pid, 5, data)

        if _.isUndefined(self._data.military):
            self._data.military = True

        if _.isUndefined(self._data.sap_ind):
            self._data.sap_ind = 0

        if self._pid != -1:
            self.room = Game.rooms[self._data.room_name]
            self.target_room = Game.rooms[self._data.target_room]

    def _run(self):
        self.run_creeps()

    def roomCallback(self, name):
        room = Game.rooms[name]

        if _.isUndefined(room):
            return

        costs = __new__(PathFinder.CostMatrix)

        for struct in room.find(FIND_STRUCTURES):
            if struct.structureType == STRUCTURE_ROAD:
                costs.set(struct.pos.x, struct.pos.y, 1)
            elif (struct.structureType != STRUCTURE_CONTAINER and
                    (struct.structureType != STRUCTURE_RAMPART or
                     not struct.my)):
                costs.set(struct.pos.x, struct.pos.y, 0xff)

        for creep in room.find(FIND_CREEPS):
            costs.set(creep.pos.x, creep.pos.y, 0xff)

        return costs

    def run_creep(self, creep):
        if _.isUndefined(creep.memory.attacking) or creep.hits == creep.hitsMax:
            creep.memory.attacking = True
        else:
            if self.room.rcl < 7 and \
                    creep.getActiveBodyparts(TOUGH) * 100 <= self.tower_damage_on_tile(creep.room, creep.pos) * 2:
                creep.memory.attacking = False
            elif self.room.rcl >= 7 and \
                    creep.getActiveBodyparts(RANGED_ATTACK) * 100 <= self.tower_damage_on_tile(creep.room, creep.pos):
                creep.memory.attacking = False

        if creep.memory.attacking:
            sapper_spots = Memory.rooms[self._data.target_room].attack.sapper_spots
            sap_spot = sapper_spots[self._data.sap_ind]

            sap_spot = __new__(RoomPosition(sap_spot.x, sap_spot.y, sap_spot.roomName))

            if not creep.pos.isNearTo(sap_spot) or not self._data.on_sap:
                # creep.say(creep.pos.getRangeTo(sap_spot))
                if creep.getActiveBodyparts(TOUGH) * 100 > self.tower_damage_on_tile(creep.room, creep.pos) * 2:
                    creep.drive_to(sap_spot)

                if creep.pos.getRangeTo(sap_spot) == 0:
                    self._data.on_sap = True
                    print("On the sap spot!")

                if creep.room == self.target_room:
                    hostile = creep.pos.findClosestByRange(self.target_room.find(FIND_HOSTILE_CREEPS))
                    if not _.isNull(hostile) and creep.pos.inRangeTo(hostile, 3):
                        creep.rangedAttack(hostile)
                    # else:
                    #     creep.rangedMassAttack()
            else:
                hostile = creep.pos.findClosestByRange(self.target_room.find(FIND_HOSTILE_CREEPS))
                creep.say(hostile)
                if _.isNull(hostile) or creep.pos.getRangeTo(hostile) > 3:
                    if creep.pos.x == 49:
                        creep.move(LEFT)
                    elif creep.pos.x == 0:
                        creep.move(RIGHT)
                    elif creep.pos.y == 49:
                        creep.move(TOP)
                    elif creep.pos.y == 0:
                        creep.move(BOTTOM)

                    # creep.rangedMassAttack()
                else:
                    creep.moveTo(sap_spot, {'maxOps': 500})
                    creep.rangedAttack(hostile)
        else:
            self._data.on_sap = False
            if creep.room.name == self._data.target_room:
                if creep.pos.x > 47:
                    res = creep.move(RIGHT)
                elif creep.pos.x < 2:
                    res = creep.move(LEFT)
                elif creep.pos.y > 47:
                    res = creep.move(BOTTOM)
                elif creep.pos.y < 2:
                    res = creep.move(TOP)

                if res != OK:
                    creep.moveTo(self.room.controller)
            elif len(creep.room.hostile_military) > 0:
                creep.drive_to(self.room.controller)
            elif creep.pos.x > 48 or creep.pos.x < 1 or \
                    creep.pos.y > 48 or creep.pos.y < 1:
                if creep.pos.x > 47:
                    creep.move(LEFT)
                elif creep.pos.x < 2:
                    creep.move(RIGHT)
                elif creep.pos.y > 47:
                    creep.move(TOP)
                elif creep.pos.y < 2:
                    creep.move(BOTTOM)
                else:
                    creep.moveTo(self.room.controller)

        my_creeps = _.filter(creep.room.find(FIND_MY_CREEPS), lambda c: c.hits < c.hitsMax
                             and c.pos.getRangeTo(creep) <= 3)
        target = creep.pos.findClosestByRange(my_creeps)

        if creep.hits < creep.hitsMax:
            creep.heal(creep)
        elif not _.isNull(target):
            if creep.pos.isNearTo(target):
                creep.heal(target)
            elif self.room.rcl < 7:
                creep.rangedHeal(target)
        elif creep.room == self.target_room:
            creep.heal(creep)

    def tower_damage_on_tile(self, room, tile):
        total_damage = 0
        for tower in room.towers:
            if tower.energy < TOWER_ENERGY_COST:
                continue

            dist = tower.pos.getRangeTo(tile)
            if dist <= TOWER_OPTIMAL_RANGE:
                total_damage += TOWER_POWER_ATTACK
            elif dist <= TOWER_FALLOFF_RANGE:
                ddist = dist - TOWER_OPTIMAL_RANGE
                fall_off = TOWER_POWER_ATTACK * TOWER_FALLOFF * (ddist / (TOWER_FALLOFF_RANGE - TOWER_OPTIMAL_RANGE))
                total_damage += TOWER_POWER_ATTACK - fall_off
            else:
                total_damage += TOWER_POWER_ATTACK * (1 - TOWER_FALLOFF)

        return total_damage

    def _needs_creeps(self, creep_names):
        return creep_names < 1

    def is_valid_creep(self, creep):
        return creep.memory.role == 'sapper'

    def gen_body(self, energy):
        if self.room.rcl < 7:
            body = [MOVE, RANGED_ATTACK, MOVE, HEAL]
            mod = [TOUGH, MOVE]
            tough_count = 1

            while self.get_body_cost(body.concat(mod)) <= energy and len(body.concat(mod)) <= 50:
                body = body.concat(mod)
                tough_count += 1  # will count ranged attack after

                if tough_count >= 10:
                    mod = [HEAL, MOVE]
        else:
            body = [HEAL, MOVE]
            mod = [HEAL, MOVE]
            heaL_count = 1

            while self.get_body_cost(body.concat(mod)) <= energy and len(body.concat(mod)) <= 50:
                body = body.concat(mod)
                heaL_count += 1  # will count ranged attack after

                if heaL_count >= 9:
                    mod = [RANGED_ATTACK, MOVE]

        return body, {'role': 'sapper'}
