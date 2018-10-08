
from defs import *  # noqa

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')
__pragma__('noalias', 'name')


class RemoteInvaderDefence(CreepProcess):

    def __init__(self, pid, data={}):
        super().__init__('remoteinvaderdefence', pid, 2, data)

        if _.isUndefined(self._data.military):
            self._data.military = True

        if self._pid != -1:
            self.room = Game.rooms[self._data.room_name]
            self.target_room = Game.rooms[self._data.target_room]

    def _run(self):
        self.run_creeps()

    def run_creep(self, creep):
        creep.say("arr!")
        if creep.room.name != self._data.target_room:
            creep.moveTo(__new__(RoomPosition(25, 25, self._data.target_room)))
        else:
            target_creeps = _.filter(creep.room.find(FIND_HOSTILE_CREEPS),
                                     lambda c: c.getActiveBodyparts(ATTACK) > 0 or
                                               c.getActiveBodyparts(RANGED_ATTACK) > 0 or
                                               c.getActiveBodyparts(HEAL) > 0)  # noqa

            if len(target_creeps) < 1:
                creep.say("Clear!")
                return

            target = creep.pos.findClosestByRange(target_creeps)
            if creep.pos.getRangeTo(target) > 3 or \
                    creep.getActiveBodyparts(RANGED_ATTACK) < target.getActiveBodyparts(RANGED_ATTACK):
                creep.moveTo(target)

            if creep.pos.inRangeTo(target, 3):
                creep.rangedAttack(target)

            if creep.pos.isNearTo(target):
                creep.attack(target)

    def needs_creeps(self):
        return len(self._data.creep_names) < 1

    def is_completed(self):
        if not self.target_room:
            return False

        if len(self.target_room.hostile_military) > 0:
            return False
        else:
            return True

    def is_valid_creep(self, creep):
        return creep.memory.role == 'invaderdefender'

    def gen_body(self, energy):
        body = [TOUGH, TOUGH, TOUGH, TOUGH, MOVE, MOVE, MOVE, MOVE, ATTACK, MOVE]
        mod = [ATTACK, MOVE]
        attack_count = 1

        while self.get_body_cost(body.concat(mod)) <= energy and attack_count < 7:
            body = body.concat(mod)
            attack_count += 1

            if attack_count >= 7:
                mod = [ATTACK, MOVE]
            elif attack_count >= 5:
                mod = [RANGED_ATTACK, MOVE]

        return body, {'role': 'invaderdefender'}
