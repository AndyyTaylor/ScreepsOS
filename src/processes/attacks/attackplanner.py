
from defs import *  # noqa
from typing import List, Union, Any

from framework.process import Process

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')


class AttackPlanner(Process):

    def __init__(self, pid, data={}):
        super().__init__('attackplanner', pid, 3, data)

        if pid != -1:
            self.target_room = Game.rooms[self._data.target_room]

            self.validate_memory()

    def _run(self) -> None:
        if _.isUndefined(self.target_room):
            if Game.time % 10 == 0:
                print("Attack:", 'no visibility on', self._data.target_room)
            return

        self.vis = self.target_room.visual

        mem = Memory.rooms[self._data.target_room].attack

        attack_sequence = self.load_attack_sequence(mem)
        path = []
        for action in attack_sequence:
            pos = __new__(RoomPosition(action.pos.x, action.pos.y, action.pos.roomName))
            path.append(pos)
            for tid in action.targets:
                if _.isNull(Game.getObjectById(tid)):
                    continue

                self.vis.line(pos, Game.getObjectById(tid).pos, {'stroke': 'red'})

        self.vis.poly(path, {'stroke': 'blue'})

    def load_attack_sequence(self, mem):
        if _.isUndefined(mem.attack_sequence):
            total_path, target_order = self.gen_attack_path(mem)

            target_ind = 0
            attack_sequence = []
            for tile in total_path:
                action: Any = {'pos': {'x': tile.x, 'y': tile.y, 'roomName': tile.roomName}, 'targets': []}
                for i in range(target_ind, len(target_order)):
                    target = target_order[i]
                    if target.pos.isNearTo(tile):
                        action['targets'].append(target.id)
                        target_ind += 1
                    else:
                        break
                attack_sequence.append(action)

            mem.attack_sequence = attack_sequence

        return mem.attack_sequence

    def gen_attack_path(self, mem):
        target_order = []

        target_types = [STRUCTURE_SPAWN, STRUCTURE_TOWER, STRUCTURE_EXTENSION, STRUCTURE_TERMINAL]
        targets = _.filter(self.target_room.find(FIND_STRUCTURES), lambda s: target_types.includes(s.structureType))

        entry_points = self.load_entry_points(mem)
        best_target, total_path = self.select_first_target(targets, entry_points)

        target_order.append(best_target)
        targets.remove(best_target)

        while len(targets) > 0:
            start = total_path[len(total_path) - 1]
            best_target, best_path = self.select_more_targets(targets, start)

            total_path = total_path.concat(best_path)
            target_order.append(best_target)
            targets.remove(best_target)

        if total_path is not None:
            total_path = self.trim_path_edges(total_path)

        return total_path, target_order

    def trim_path_edges(self, path):
        edge_walk = 0
        for tile in path:
            if tile.x == 1 or tile.x == 48 or tile.y == 1 or tile.y == 48:
                edge_walk += 1
            else:
                break

        path = path[max(0, edge_walk - 1):]

        return path

    def select_first_target(self, targets: List[RoomObject], entry_points: List[RoomPosition]) -> \
            (RoomPosition, List[RoomPosition]):
        best_target = None
        best_path = None
        best_wall_hits = 0
        best_callback_index = 0
        for entry in entry_points:
            for target in targets:
                path, walls, callback_index = self.get_path_to(entry, target)

                wall_hits = 0
                for wall in walls:
                    wall_hits += wall.hits
                # print('Target at ({}, {}) has {} walls in the way'.format(tower.pos.x, tower.pos.y, len(walls)))
                if best_target is None or callback_index < best_callback_index or \
                        (callback_index == best_callback_index and wall_hits < best_wall_hits) or \
                        (callback_index == best_callback_index and wall_hits == best_wall_hits and
                         len(path) < len(best_path)):
                    best_target = target
                    best_path = path
                    best_wall_hits = wall_hits
                    best_callback_index = callback_index

        return best_target, best_path

    def select_more_targets(self, targets: List[RoomObject], start: RoomPosition):
        best_target = None
        best_path = None
        best_wall_hits = 0
        best_callback_index = 0

        for target in targets:
            path, walls, callback_index = self.get_path_to(start, target)

            wall_hits = 0
            for wall in walls:
                wall_hits += wall.hits

            if best_target is None or callback_index < best_callback_index or \
                    (callback_index == best_callback_index and wall_hits < best_wall_hits) or \
                    (callback_index == best_callback_index and wall_hits == best_wall_hits and
                     len(path) < len(best_path)):
                best_target = target
                best_path = path
                best_wall_hits = wall_hits
                best_callback_index = callback_index

        return best_target, best_path

    def get_path_to(self, start: RoomPosition, target: RoomObject) -> \
            (List[RoomPosition], List[Union[StructureWall, StructureRampart]], int):
        callbacks = [self.basic_callback, self.very_lonely_wall_callback, self.lonely_wall_callback]
        index = 0
        for callback in callbacks:
            ret = PathFinder.search(start, {'pos': target.pos, 'range': 1},
                                    {'maxRooms': 1, 'plainCost': 2, 'spawnCost': 10,
                                     'roomCallback': callback})

            if not ret.incomplete:
                return ret.path, self.find_walls_on_path(ret.path), index

            index += 1

        print('callbacks failed, pleas implement kamikaze callback')

        ret = PathFinder.search(start, {'pos': target.pos, 'range': 1},
                                {'maxRooms': 1, 'plainCost': 1, 'spawnCost': 5,
                                 'roomCallback': self.basic_callback})

        return ret.path, [], len(callbacks)

    def load_targets(self):
        targets = []
        for tower in self.target_room.towers:
            targets.append(tower)
        for spawn in self.target_room.spawns:
            targets.append(spawn)

        return targets

    def find_walls_on_path(self, path: List[RoomPosition]) -> List[Union[StructureWall, StructureRampart]]:
        walls = []
        for pos in path:
            structs = self.target_room.lookForAt(LOOK_STRUCTURES, pos)
            for struct in structs:
                if struct.structureType == STRUCTURE_WALL or struct.structureType == STRUCTURE_RAMPART:
                    walls.append(struct)

        return walls

    def basic_callback(self, room_name):
        room = Game.rooms[room_name]

        if not room:
            return

        costs = __new__(PathFinder.CostMatrix)

        for struct in room.find(FIND_STRUCTURES):
            if struct.structureType != STRUCTURE_CONTAINER and struct.structureType != STRUCTURE_ROAD:
                costs.set(struct.pos.x, struct.pos.y, 0xff)

        return costs

    def lonely_wall_callback(self, room_name):
        room = Game.rooms[room_name]

        if not room:
            return

        max_hits = 0
        for wall in room.walls:
            if wall.hits > max_hits:
                max_hits = wall.hits

        costs = __new__(PathFinder.CostMatrix)

        for struct in room.find(FIND_STRUCTURES):
            if struct.structureType == STRUCTURE_WALL:
                nearby_rampart = False
                for nearby_struct in room.lookForAtArea(LOOK_STRUCTURES,
                                                        struct.pos.y - 1, struct.pos.x - 1,
                                                        struct.pos.y + 1, struct.pos.x + 1, True):
                    if nearby_struct.structure.structureType == STRUCTURE_RAMPART:
                        nearby_rampart = True
                        break

                if nearby_rampart:
                    costs.set(struct.pos.x, struct.pos.y, 0xff)
                else:
                    costs.set(struct.pos.x, struct.pos.y, 10 + 200 * (struct.hits / max_hits))
            elif struct.structureType != STRUCTURE_CONTAINER and struct.structureType != STRUCTURE_ROAD:
                costs.set(struct.pos.x, struct.pos.y, 0xff)

        return costs

    def very_lonely_wall_callback(self, room_name):
        room = Game.rooms[room_name]

        if not room:
            return

        costs = __new__(PathFinder.CostMatrix)

        max_hits = 0
        for wall in room.walls:
            if wall.hits > max_hits:
                max_hits = wall.hits

        for struct in room.find(FIND_STRUCTURES):
            if struct.structureType == STRUCTURE_WALL:
                nearby_rampart = False
                top = max(0, struct.pos.y - 3)
                left = max(0, struct.pos.x - 3)
                bottom = min(49, struct.pos.y + 3)
                right = min(49, struct.pos.x + 3)
                for nearby_struct in room.lookForAtArea(LOOK_STRUCTURES, top, left, bottom, right, True):
                    if nearby_struct.structure.structureType == STRUCTURE_RAMPART:
                        nearby_rampart = True
                        break

                if nearby_rampart:
                    costs.set(struct.pos.x, struct.pos.y, 0xff)
                else:
                    costs.set(struct.pos.x, struct.pos.y, 10 + 200 * (struct.hits / max_hits))
            elif struct.structureType != STRUCTURE_CONTAINER and struct.structureType != STRUCTURE_ROAD:
                costs.set(struct.pos.x, struct.pos.y, 0xff)

        return costs

    def load_entry_points(self, mem) -> List[RoomPosition]:
        if _.isUndefined(mem.entries):
            mem.entries = []
            unique_exits = []
            tested = []
            exit_tiles = self.target_room.find(FIND_EXIT)
            for exit in exit_tiles:
                unique = True
                for tile in tested:
                    if tile.isNearTo(exit):
                        unique = False
                        break

                if unique:
                    unique_exits.append(exit)

                tested.append(exit)

            for entry in unique_exits:
                mem.entries.append({'x': entry.x, 'y': entry.y, 'roomName': entry.roomName})

        entry_points = []
        for entry in mem.entries:
            entry_points.append(__new__(RoomPosition(entry.x, entry.y, entry.roomName)))

        return entry_points

    def validate_memory(self):
        if _.isUndefined(Memory.rooms[self._data.target_room]):
            Memory.rooms[self._data.target_room] = {}

        if _.isUndefined(Memory.rooms[self._data.target_room].attack):
            Memory.rooms[self._data.target_room].attack = {}
