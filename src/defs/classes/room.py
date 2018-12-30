from typing import Any, Callable, Dict, List, Optional, Type, Union

# noinspection PyProtectedMember
from .memory import _Memory
from .misc_obj import RoomObject, Source, Mineral
from .structures import StructureController, StructureStorage, StructureTerminal, StructureSpawn, StructureTower, StructureWall, StructureRampart, ConstructionSite, Structure
from ..transcrypt import Uint8Array

_HasPosition = Union['RoomPosition', 'RoomObject']
_FindParameter = Union[int, List[_HasPosition]]


# noinspection PyPep8Naming
class RoomPosition:
    """
    :type x: int
    :type y: int
    :type roomName: str
    :type prototype: Type[RoomPosition]
    """
    prototype = None  # type: Type[RoomPosition]

    def __init__(self, x: int, y: int, roomName: str) -> None:
        """
        NOTE: In order to use this, you must surround it with `__new__`: `__new__(RoomPosition(x, y, roomName))`
        """
        self.x = x
        self.y = y
        self.roomName = roomName

    def createConstructionSite(self, structureType: str) -> int:
        pass

    def createFlag(self, name: str = None, color: int = None, secondaryColor: int = None) -> Union[str, int]:
        pass

    def findClosestByPath(self, source: _FindParameter, opts: Optional[Dict[str, Any]] = None) -> Optional[RoomObject]:
        pass

    def findClosestByRange(self, source: _FindParameter, opts: Optional[Dict[str, Any]] = None) -> Optional[RoomObject]:
        pass

    def findInRange(self, source: _FindParameter, _range: int, opts: Optional[Dict[str, Any]] = None) \
            -> List[RoomObject]:
        pass

    def getDirectionTo(self, x: Union[int, 'RoomPosition', RoomObject], y: int = None) -> int:
        pass

    def getRangeTo(self, x: Union[int, 'RoomPosition', RoomObject], y: int = None) -> int:
        pass

    def inRangeTo(self, x: Union[int, 'RoomPosition', RoomObject], y_or_range: int = None,
                  _range: int = None) -> bool:
        pass

    def isEqualTo(self, x: Union[int, 'RoomPosition', RoomObject], y: int = None) -> bool:
        pass

    def isNearTo(self, x: Union[int, 'RoomPosition', RoomObject], y: int = None) -> bool:
        pass

    def look(self) -> List[Dict[str, Any]]:
        pass

    def lookFor(self, _type: str) -> List[RoomObject]:
        pass


RoomPosition.prototype = RoomPosition


# noinspection PyPep8Naming
class _Event:
    """
    :type event: int
    :type objectId: str
    :type data: Dict[str, Any]
    """

    def __init__(self, event: int, objectId: str, data: Dict[str, Any]) -> None:
        """
        WARNING: This constructor is purely for type completion, and does not exist in the game.
        """
        self.event = event  # type: int
        self.objectId = objectId  # type: str
        self.data = data  # type: Dict[str, Any]


class _Owner:
    """
    :type username: str
    """

    def __init__(self, username: str) -> None:
        """
        WARNING: This constructor is purely for type completion, and does not exist in the game.
        """
        self.username = username


class _PathPos:
    """
    :type x: int
    :type y: int
    :type dx: int
    :type dy: int
    :type direction: int
    """

    def __init__(self, x: int, y: int, dx: int, dy: int, direction: int) -> None:
        """
        WARNING: This constructor is purely for type completion, and does not exist in the game.
        """
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.direction = direction


# noinspection PyPep8Naming
class Room:
    """
    :type controller: Optional[StructureController]
    :type storage: Optional[StructureStorage]
    :type terminal: Optional[StructureTerminal]
    :type energyAvailable: int
    :type energyCapacityAvailable: int
    :type memory: Any
    :type mode: str
    :type name: str
    :type visual: Any
    :type rcl: int
    :type damaged_walls: List[Union[StructureWall, StructureRampart]]
    :type construction_sites: List[ConstructionSite]
    """

    spawns: List[StructureSpawn] = None
    towers: List[StructureTower] = None

    # noinspection PyPep8Naming
    class Terrain:
        """
        :type roomName: str
        """

        def __init__(self, roomName: str) -> None:
            """
            WARNING: This constructor is purely for type completion, and does not exist in the game.
            """
            self.roomName = roomName

        def get(self, x: int, y: int) -> int:
            pass

        def getRawBuffer(self, destinationArray: Optional[Uint8Array]) -> None:
            pass

    def __init__(self, controller: Optional[StructureController], storage: Optional[StructureStorage],
                 terminal: Optional[StructureTerminal], energyAvailable: int, energyCapacityAvailable: int,
                 memory: Any, mode: str, name: str, visual: Any, rcl: int, 
                 damaged_walls: List[Union[StructureWall, StructureRampart]],
                 construction_sites: List[ConstructionSite], repair_sites: List[Structure],
                 sources: List[Source], mineral: Mineral) -> None:
        """
        WARNING: This constructor is purely for type completion, and does not exist in the game.
        """
        self.controller = controller  # type: Optional[StructureController]
        self.storage = storage  # type: Optional[StructureStorage]
        self.terminal = terminal  # type: Optional[StructureTerminal]
        self.energyAvailable = energyAvailable  # type: int
        self.energyCapacityAvailable = energyCapacityAvailable  # type: int
        self.memory = memory  # type: Any
        self.mode = mode  # type: str
        self.name = name  # type: str
        self.visual = visual  # type: Any
        self.rcl = rcl  # type: int
        self.damaged_walls = damaged_walls  # type: List[Union[StructureWall, StructureRampart]]
        self.construction_sites = construction_sites  # type: List[ConstructionSite]
        self.repair_sites = repair_sites  # type: List[Structure]
        self.sources = sources  # type: List[Source]
        self.mineral = mineral  # type: Mineral

    @classmethod
    def serializePath(cls, path: List[Union[_PathPos, Dict[str, Any], RoomPosition]]) -> str:
        pass

    @classmethod
    def deserializePath(cls, path: str) -> List[_PathPos]:
        pass

    def createConstructionSite(self, x: Union[int, RoomPosition, RoomObject], y: Union[int, str],
                               structureType: str = None) -> int:
        pass

    def createFlag(self, pos: Union[RoomPosition, RoomObject], name: str = None, color: int = None,
                   secondaryColor: int = None) -> Union[str, int]:
        pass

    def find(self, _type: _FindParameter,
             opts: Optional[Dict[str, Union[Callable[[RoomObject], bool], Dict[str, Any]]]] = None) \
            -> List[RoomObject]:
        pass

    def findExitTo(self, room: str) -> int:
        pass

    def findPath(self, fromPos: RoomPosition, toPos: RoomPosition, opts: Dict[str, Any]) \
            -> List[Union[_PathPos, Dict[str, Any]]]:
        pass

    def get_additional_workers(self) -> int:
        pass

    def getEventLog(self, raw: bool = False) -> List[_Event]:
        pass

    def getPositionAt(self, x: int, y: int) -> RoomPosition:
        pass

    def getTerrain(self) -> 'Room.Terrain':
        pass

    def is_city(self) -> bool:
        pass

    def is_full(self) -> bool:
        pass

    def is_remote(self) -> bool:
        pass

    def lookAt(self, x: Union[int, RoomPosition, RoomObject], y: int = None) -> List[Dict[str, Any]]:
        pass

    def lookAtArea(self, top: int, left: int, bottom: int, right: int, asArray: bool = False) \
            -> Union[List[Dict[str, Any]], Dict[int, Dict[int, Dict[str, Any]]]]:
        pass

    def lookForAt(self, _type: str, x: Union[int, RoomPosition, RoomObject], y: int = None) -> List[RoomObject]:
        pass

    def lookForAtArea(self, _type: str, top: int, left: int, bottom: int, right: int, asArray: bool = False) \
            -> Union[List[Dict[str, RoomObject]], Dict[int, Dict[int, Dict[str, RoomObject]]]]:
        pass
