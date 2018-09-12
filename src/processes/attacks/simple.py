
from defs import *  # noqa

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')
__pragma__('noalias', 'name')


class SimpleAttack(CreepProcess):

    def __init__(self, pid, data={}):
        super().__init__('simpleattack', pid, 2, data)

        if _.isUndefined(self._data.military):
            self._data.military = True

        if self._pid != -1:
            self.room = Game.rooms[self._data.room_name]

    def _run(self):
        self.target_room = Game.rooms[self._data.target_room]

        self.run_creeps()

    def run_creep(self, creep):
        has_attacked = False
        if _.isUndefined(creep.memory.attacking) or creep.hits == creep.hitsMax:
            creep.memory.attacking = True
        elif creep.hits < creep.hitsMax * 0.7:
            creep.memory.attacking = False
        creep.say(creep.memory.attacking)
        if creep.memory.attacking:
            if _.isUndefined(self.target_room) or creep.room != self.target_room:
                creep.moveTo(__new__(RoomPosition(25, 25, self._data.target_room)))
            else:
                target_creeps = _.filter(creep.room.find(FIND_HOSTILE_CREEPS),
                                         lambda c: c.getActiveBodyparts(ATTACK) > 0 or
                                         c.getActiveBodyparts(RANGED_ATTACK) > 0 or
                                         c.getActiveBodyparts(HEAL) > 0)

                is_creep = False
                if len(target_creeps) > 0:
                    target = creep.pos.findClosestByRange(target_creeps)
                    is_creep = True
                    if not creep.pos.inRangeTo(target, 3):
                        target = None
                        is_creep = False

                if _.isUndefined(target) or target is None:
                    if len(creep.room.spawns) > 0:
                        target = creep.pos.findClosestByRange(creep.room.spawns)
                    else:
                        structures = _.filter(creep.room.find(FIND_STRUCTURES), lambda s:
                                              s.structureType != STRUCTURE_ROAD and
                                              s.structureType != STRUCTURE_WALL and
                                              s.structureType != STRUCTURE_RAMPART)
                        if len(structures) > 0:
                            target = creep.pos.findClosestByRange(structures)

                if not _.isUndefined(target):
                    if is_creep:
                        if target.getActiveBodyparts(RANGED_ATTACK) > 0 or \
                                creep.getActiveBodyparts(RANGED_ATTACK) == 0:
                            creep.moveTo(target)
                    else:
                        creep.moveTo(target)

                    if creep.pos.isNearTo(target):
                        if creep.getActiveBodyparts(ATTACK) > 0:
                            creep.attack(target)
                            has_attacked = True

                        creep.rangedMassAttack()
                    elif creep.pos.inRangeTo(target, 3):
                        creep.rangedAttack(target)
        else:
            if creep.room.name == self._data.target_room or creep.pos.x > 47 or creep.pos.x < 3 or \
                    creep.pos.y > 47 or creep.pos.y < 3:
                creep.moveTo(self.room.controller)

            target_creeps = _.filter(creep.room.find(FIND_HOSTILE_CREEPS),
                                     lambda c: c.getActiveBodyparts(ATTACK) > 0 or
                                     c.getActiveBodyparts(RANGED_ATTACK) > 0 or
                                     c.getActiveBodyparts(HEAL) > 0)

            if len(target_creeps) > 0:
                target = creep.pos.findClosestByRange(target_creeps)
                if not creep.pos.inRangeTo(target, 3):
                    target = None

                if target is not None:
                    if creep.pos.isNearTo(target):
                        creep.rangedMassAttack()
                    elif creep.pos.inRangeTo(target, 3):
                        creep.rangedAttack(target)

        if not has_attacked:
            creep.heal(creep)

        creep.run_current_task()

    def needs_creeps(self):
        if Game.time < 9408551 + 5000:
            return len(self._data.creep_names) < 1
        else:
            return False

    def is_valid_creep(self, creep):
        return creep.getActiveBodyparts(ATTACK) > 0 or creep.getActiveBodyparts(RANGED_ATTACK) > 0

    def gen_body(self, energy):
        body = [ATTACK, MOVE, MOVE, HEAL]
        mod = [ATTACK, MOVE]
        attack_count = 1

        while self.get_body_cost(body.concat(mod)) <= energy:
            body = body.concat(mod)
            attack_count += 1  # will count ranged attack after

            if attack_count >= 8:
                mod = [RANGED_ATTACK, MOVE]

        return body, None