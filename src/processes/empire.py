
import config
from defs import *  # noqa
# from extends import *  # noqa
from base import base
from typing import Tuple

from framework.process import Process

__pragma__('noalias', 'keys')
__pragma__('noalias', 'values')


class Empire(Process):

    def __init__(self, pid: int, data=None) -> None:
        super().__init__("empire", pid, 1, data)

    def _run(self) -> None:
        self.cities: List[str] = self.launch_cities()

        if Game.time % 100 == 0:
            self.create_scout_tasks()
        
        if self.should_expand():
            self.plan_expansion()
        
        self.assign_remote_work()
    
    def assign_remote_work(self) -> None:
        needs_help = []
        for city in self.cities:
            if Game.rooms[city].rcl < 3:  # TODO: more complex based on being attacked etc
                needs_help.append(city)
        
        for city in needs_help:
            closest_city, _ = self.get_closest_city(city, 3)
            if not Memory.rooms[closest_city].to_work.includes(city):
                Memory.rooms[closest_city].to_work.append(city)
    
    def should_expand(self) -> bool:
        if Game.gcl.level <= len(self.cities):
            return False
        
        lowest_rcl = 8
        for room in self.cities:
            if Game.rooms[room].rcl < lowest_rcl:
                lowest_rcl = Game.rooms[room].rcl
        
        if lowest_rcl < 3:
            return False
        
        return True
    
    def plan_expansion(self) -> None:
        claimable = _.filter(Object.keys(Memory.rooms), lambda r: Memory.rooms[r].scout_info and 
                                                                  Memory.rooms[r].scout_info.num_sources == 2 and
                                                                  Memory.rooms[r].scout_info.claimable and
                                                                  Memory.rooms[r].scout_info.fits_base)
        
        not_too_close = []
        for room in claimable:
            too_close = False
            closest_dist = 99
            closest_city = None
            for city in self.cities:
                dist = Game.map.getRoomLinearDistance(room, city)

                if dist < closest_dist:
                    closest_dist = dist
                    closest_city = city

                if dist < 2:
                    too_close = True
                    break
            
            if not too_close:
                not_too_close.append((room, closest_dist, closest_city))

        closest = None
        best_dist = 999
        closest_city = None
        for room, dist, city in not_too_close:
            if dist < best_dist:
                closest = room
                best_dist = dist
                closest_city = city

        if not Memory.rooms[closest_city].to_claim.includes(closest):
            Memory.rooms[closest_city].to_claim.append(closest)
        
        print("Claiming", Memory.rooms[closest_city].to_claim, 'from', closest_city)
    
    def create_scout_tasks(self) -> None:
        cur_dist = 0
        past_rooms = []
        cur_rooms = [].concat(self.cities)

        while cur_dist < MAX_SCOUT_RANGE:
            cur_dist += 1

            new_rooms = []
            for room in cur_rooms:
                exits = Game.map.describeExits(room)
                if _.isUndefined(exits) or _.isNull(exits):
                    continue

                new_rooms = new_rooms.concat(Object.values(exits))
            
            new_rooms = _.filter(new_rooms, lambda r: not past_rooms.includes(r))
            
            for room in new_rooms:
                scout_freq = SCOUT_FREQ(cur_dist)

                if self.should_scout(room, scout_freq):
                    city, d = self.get_closest_city(room)
                    if not Memory.rooms[city].to_scout.includes(room):
                        Memory.rooms[city].to_scout = Memory.rooms[city].to_scout.concat([room])

            past_rooms = past_rooms.concat(cur_rooms)
            cur_rooms = new_rooms
        
    def get_closest_city(self, room: str, min_rcl: int=0) -> Tuple[str, int]:
        min_dist = 999
        best_city = None
        for city in self.cities:
            dist = Game.map.getRoomLinearDistance(city, room)
            if dist < min_dist and Game.rooms[city].rcl >= min_rcl:
                best_city = city
                min_dist = dist

        return best_city, min_dist
    
    def should_scout(self, room: str, scout_freq: int):
        mem = Memory.rooms[room]

        if not Game.map.isRoomAvailable(room):
            return False

        # ? More complex conditions re players etc?
        if _.isUndefined(mem) or _.isUndefined(mem.last_updated) or mem.last_updated + scout_freq < Game.time:
            return True
        
        return False

    def launch_cities(self) -> List[str]:
        """ Launches a process for each city """
        cities = []

        for room_name in Object.keys(Game.rooms):
            room = Game.rooms[room_name]

            if room.is_city():
                cities.append(room_name)

        if self.scheduler.count_by_name('city') < len(cities):
            taken_cities = []
            for proc in self.scheduler.proc_by_name('city'):
                taken_cities.append(proc['data'].main_room)

            for city in cities:
                if not taken_cities.includes(city):
                    self.scheduler.launch_process('city', {'main_room': city})

        return cities
