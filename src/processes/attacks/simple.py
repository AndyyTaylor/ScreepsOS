
from defs import *  # noqa
from typing import Optional

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')
__pragma__('noalias', 'name')


class SimpleAttack(CreepProcess):

    def __init__(self, pid, data=None):
        super().__init__('simpleattack', pid, 5, data)

        if _.isUndefined(self._data.military):
            self._data.military = True

        if _.isUndefined(self._data.red_team):
            self._data.red_team = False

        if self._pid != -1:
            self.room = Game.rooms[self._data.room_name]
            self.target_room = Game.rooms[self._data.target_room]

    def run_creep(self, creep):
        self.set_attacking_status(creep)

        if self._data.red_team and (creep.room == self.target_room or creep.memory.red_team):
            creep.memory.red_team = True
            hostile_military = _.filter(creep.room.find(FIND_CREEPS), lambda c: _.isUndefined(c.memory.red_team))
        else:
            hostile_military = creep.room.hostile_military

        has_attacked = False
        if creep.memory.attacking:
            if creep.room != self.target_room:
                if len(hostile_military) == 0 or creep.distToClosest(hostile_military) > 4:
                    creep.moveTo(__new__(RoomPosition(25, 25, self._data.target_room)), {'maxOps': 5000, 'range': 20})
                else:
                    has_attacked = self.attack_creep(creep, creep.pos.findClosestByRange(hostile_military))
            else:
                if len(hostile_military) > 0 and creep.distToClosest(hostile_military) <= 3:
                    print("Attacking at range", creep.distToClosest(hostile_military))
                    has_attacked = self.attack_creep(creep, creep.pos.findClosestByRange(hostile_military))
                else:
                    target_struct = self.find_target_struct(creep)
                    # print("Should kill", target_struct)
                    if target_struct is not None:
                        has_attacked = self.attack_structure(creep, target_struct)  # TODO: These should be in Creep
        else:
            if creep.room.name == self._data.target_room or creep.pos.x > 48 or creep.pos.x < 2 or \
                    creep.pos.y > 48 or creep.pos.y < 2 or len(hostile_military) > 0:
                creep.moveTo(self.room.controller)

            if len(hostile_military) > 0:
                target = creep.pos.findClosestByRange(hostile_military)

                if target is not None:
                    if creep.pos.isNearTo(target):
                        creep.rangedMassAttack()
                    elif creep.pos.inRangeTo(target, 3):
                        creep.rangedAttack(target)

        if not has_attacked:
            if len(creep.room.walls) > 0 and \
                    creep.distToClosest(creep.room.walls) == 1:
                creep.attack(creep.pos.findClosestByRange(creep.room.walls))
            else:
                creep.heal(creep)

        creep.run_current_task()

    def find_target_struct(self, creep: Creep) -> Optional[Structure]:
        destroy_order = [STRUCTURE_TOWER, STRUCTURE_SPAWN, STRUCTURE_EXTENSION, STRUCTURE_TERMINAL, STRUCTURE_RAMPART]
        best_target = None
        best_priority = 0

        total = 0
        for struct in self.target_room.find(FIND_STRUCTURES):
            struct_priority = destroy_order.index(struct.structureType)
            if struct_priority == -1:
                continue

            if best_target is None or struct_priority < best_priority:
                # start = Game.cpu.getUsed()
                results = PathFinder.search(creep.pos,
                                            {'pos': struct.pos, 'range': 1},
                                            {'roomCallback': self.basic_callback,
                                             'maxRooms': 1})
                # print(Game.cpu.getUsed() - start)
                if results.incomplete:
                    continue

                best_target = struct
                best_priority = struct_priority
        # print(total)  TODO: Work out the best way to cast a variable for minimal cpu

        return best_target

    def basic_callback(self, room_name: str):
        room = Game.rooms[room_name]

        if not room:
            return

        if _.isUndefined(self._data.cost_matrix) or Game.time % 200 == 0:
            costs = __new__(PathFinder.CostMatrix)

            for struct in room.find(FIND_STRUCTURES):
                if struct.structureType != STRUCTURE_CONTAINER and struct.structureType != STRUCTURE_ROAD:
                    costs.set(struct.pos.x, struct.pos.y, 0xff)

            self._data.cost_matrix = costs
        # else:
            # print("Loading matrix from cache")

        return self._data.cost_matrix

    @staticmethod
    def attack_creep(creep: Creep, target: Creep) -> bool:
        if creep.pos.isNearTo(target) and creep.getActiveBodyparts(ATTACK) > 0:
            creep.moveTo(target)
            creep.attack(target)
            creep.rangedMassAttack()
            return True

        if creep.pos.inRangeTo(target, 3):
            creep.rangedAttack(target)

        creep_attack_parts = creep.getActiveBodyparts(ATTACK)
        target_attack_parts = target.getActiveBodyparts(ATTACK)
        if creep.pos.getRangeTo(target) > 3 or creep_attack_parts > target_attack_parts:
            creep.moveTo(target)

        return False

    @staticmethod
    def attack_structure(creep: Creep, target: Structure) -> bool:
        if creep.pos.isNearTo(target):
            creep.attack(target)
            creep.rangedMassAttack()
            return True

        if creep.pos.inRangeTo(target, 3):
            creep.rangedAttack(target)

        creep.moveTo(target, {'maxRooms': 1})
        return False

    @staticmethod
    def set_attacking_status(creep: Creep) -> None:
        if _.isUndefined(creep.memory.attacking) or creep.hits == creep.hitsMax:
            creep.memory.attacking = True
        elif creep.hits < creep.hitsMax * 0.7:
            creep.memory.attacking = False

    def needs_creeps(self):
        return len(self._data.creep_names) < 1

    def is_valid_creep(self, creep):
        return creep.memory.role == 'simpleattacker'

    def gen_body(self, energy):
        body = [ATTACK, MOVE, MOVE, HEAL]
        mod = [ATTACK, MOVE]
        attack_count = 1

        while self.get_body_cost(body.concat(mod)) <= energy and len(body.concat(mod)) <= 50:
            body = body.concat(mod)
            attack_count += 1  # will count ranged attack after

            if attack_count >= 8:
                mod = [RANGED_ATTACK, MOVE]

        return body, {'role': 'simpleattacker'}
