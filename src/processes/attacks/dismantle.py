
import random
from defs import *  # noqa

from framework.creepprocess import CreepProcess

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')
__pragma__('noalias', 'name')


class Dismantle(CreepProcess):

    def __init__(self, pid, data={}):
        super().__init__('dismantle', pid, 5, data)

        if _.isUndefined(self._data.military):
            self._data.military = True

        if _.isUndefined(self._data.target_id):
            self._data.target_id = None

        if _.isUndefined(self._data.attacking):
            self._data.attacking = True

        if _.isUndefined(self._data.should_respawn):
            self._data.should_respawn = True

        if _.isUndefined(self._data.target_pos):
            self._data.target_pos = {'x': 6, 'y': 44, 'roomName': self._data.target_room}

        if self._pid != -1:
            self.room = Game.rooms[self._data.room_name]
            self.target_room = Game.rooms[self._data.target_room]

    def _run(self):
        self.run_creeps()  # Updates expired creeps etc
        self.load_creeps()

        # print(self._data.should_respawn)
        if self.dismantler is None and self.healer is None:
            self._data.should_respawn = True
        elif self.dismantler is not None and self.healer is not None:
            self._data.should_respawn = False

        if self.dismantler is None or _.isNull(self.dismantler) or self.healer is None or _.isNull(self.healer):
            # print("Not enough creeps :(")
            return

        MAX_DAMAGE = 0.8
        # self.dismantler.say(str(self._data.attacking))

        if self.dismantler.hits < self.dismantler.hitsMax * MAX_DAMAGE or \
                self.healer.hits < self.healer.hitsMax * MAX_DAMAGE:
            self._data.attacking = False
        elif self.dismantler.hits == self.dismantler.hitsMax and self.healer.hits == self.healer.hitsMax:
            self._data.attacking = True

        target = Game.getObjectById(self._data.target_id)
        if (self._data.target_id is None or _.isNull(target) or _.isUndefined(target)) and \
                self.dismantler.room == self.target_room:
            self._data.target_id = self.dismantler.pos.findClosestByRange(self.target_room.find(FIND_STRUCTURES)).id
            print(self._data.target_id, 'chosen')
            target = Game.getObjectById(self._data.target_id)
            self._data.target_pos = {'x': target.pos.x, 'y': target.pos.y,  'roomName': target.pos.roomName}

        if _.isNull(target) or _.isUndefined(target):
            target = {'pos': __new__(RoomPosition(self._data.target_pos.x, self._data.target_pos.y, self._data.target_pos.roomName))}

        # self.healer.say(target)
        # print(JSON.stringify(target))

        # print(self._data.target_pos)
        if not self._data.attacking:
            target = self.room.controller

        if not _.isNull(target):
            if self._data.attacking:
                self.follow_leader(self.dismantler, self.healer, target)
            elif self.dismantler.room == self.target_room or self.healer.room == self.target_room or \
                    self.on_exit(self.dismantler) or self.on_exit(self.healer):
                self.follow_leader(self.healer, self.dismantler, target)

            if self.dismantler.pos.isNearTo(target):
                self.dismantler.dismantle(target)

            attacked = False
            if not _.isUndefined(self.target_room):
                hostile = self.dismantler.pos.findClosestByRange(self.target_room.find(FIND_HOSTILE_CREEPS))
                if not _.isNull(hostile) and hostile and self.dismantler.pos.isNearTo(hostile):
                    self.dismantler.rangedMassAttack()
                    attacked = True
                elif not _.isNull(hostile) and self.dismantler.pos.inRangeTo(hostile, 3):
                    self.dismantler.rangedAttack(hostile)
                    attacked = True

            if attacked:
                pass
            elif self.dismantler.pos.isNearTo(target) and target.structureType != STRUCTURE_WALL:
                self.dismantler.rangedMassAttack()
            elif self.dismantler.pos.inRangeTo(target, 3):
                self.dismantler.rangedAttack(target)

        if self.healer.hits < self.healer.hitsMax:
            self.healer.heal(self.healer)
        elif self.dismantler.hits < self.dismantler.hitsMax:
            self.healer.heal(self.dismantler)
        else:
            # self.healer.heal(random.choice([self.healer, self.dismantler]))
            self.healer.heal(self.healer)

    def follow_leader(self, leader, follower, target):
        at_target = False
        on_exit = self.on_exit(leader)
        if (follower.pos.isNearTo(leader) or on_exit) and follower.fatigue == 0:
            if not leader.pos.isNearTo(target):
                leader.moveTo(target)
            else:
                at_target = True

        if follower.fatigue == 0:
            if not follower.pos.isNearTo(leader) or not at_target:
                follower.moveTo(leader)
            elif self.on_exit(follower):
                direction = follower.pos.getDirectionTo(leader)
                if direction == RIGHT:
                    follower.move(BOTTOM_RIGHT)
                elif direction == BOTTOM_RIGHT or direction == TOP_RIGHT:
                    follower.move(RIGHT)
                elif direction == TOP:
                    follower.move(TOP_RIGHT)
                elif direction == TOP_RIGHT or direction == TOP_LEFT:
                    follower.move(TOP)

    def load_creeps(self):
        self.dismantler = None
        self.healer = None
        for name in self._data.creep_names:
            if _.isUndefined(Game.creeps[name]):
                continue

            if Game.creeps[name].memory.role == 'dismantler':
                self.dismantler = Game.creeps[name]
            elif Game.creeps[name].memory.role == 'healer':
                self.healer = Game.creeps[name]

    def on_exit(self, creep):
        return creep.pos.y == 0 or creep.pos.y == 49 or creep.pos.x == 0 or creep.pos.x == 49

    def needs_creeps(self):
        if not self._data.should_respawn:
            return False

        return len(self._data.creep_names) < 2

    def is_valid_creep(self, creep):
        self.load_creeps()

        if self.dismantler is None and creep.memory.role == 'dismantler':
            return True
        elif self.healer is None and creep.memory.role == 'healer':
            return True

        return False

    def gen_body(self, energy):
        self.load_creeps()

        if self.dismantler is None:
            body = [RANGED_ATTACK, RANGED_ATTACK, RANGED_ATTACK, RANGED_ATTACK, MOVE, MOVE, MOVE, MOVE]
            mod = [WORK, MOVE]

            while self.get_body_cost(body.concat(mod)) <= energy and len(body.concat(mod)) <= 50:
                body = body.concat(mod)

            return body, {'role': 'dismantler'}
        else:
            body = [TOUGH, TOUGH, TOUGH, MOVE, MOVE, MOVE, HEAL, MOVE]
            mod = [HEAL, MOVE]

            while self.get_body_cost(body.concat(mod)) <= energy and len(body.concat(mod)) <= 50:
                body = body.concat(mod)

            return body, {'role': 'healer'}
