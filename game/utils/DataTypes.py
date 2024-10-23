from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field
import math

@dataclass
class Point:
    x: float = 0.0
    y: float = 0.0

    def __le__(self, other: Point) -> bool:
        return self.x <= other.x and self.y <= other.y

    def __ge__(self, other: Point) -> bool:
        return self.x >= other.x and self.y >= other.y

    def __lt__(self, other: Point) -> bool:
        return self.x < other.x and self.y < other.y

    def __add__(self, other: Point) -> Point:
        x = self.x + other.x
        y = self.y + other.y
        return Point(x, y)

    def __str__(self) -> str:
        return f'[{self.x:.1f}, {self.y:.1f}]'

    def __eq__(self, other: Point):
        return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)

    def to_list(self):
        return [self.x, self.y]

    @staticmethod
    def measure_distance(a: Point, b: Point) -> float:

        squared_distance = (b.x - a.x) ** 2 + (b.y - a.y) ** 2
        return math.sqrt(squared_distance)

@dataclass
class Offset:
    dx: float = 0.0
    dy: float = 0.0

@dataclass
class LootInfo:
    id: int  = 0
    type: int = 0
    x: float = 0
    y: float = 0

LootList = list[LootInfo]

Dimension = float
Coord = Dimension

class RoadType(Enum):
    HORIZONTAL = 1
    VERTICAL = 2

class RoadMutualPositionType(int, Enum):
    Parallel = 1
    Adjacent = 2
    Crossed = 3

@dataclass
class RoadInfo:
    road_index: int
    road_type: RoadMutualPositionType


AdjacentRoads = list[list[RoadMutualPositionType]]

@dataclass(frozen=True)
class Office:
    id: str
    position: Point
    offset: Offset

@dataclass(frozen=True)
class Loot:
    name: str
    file: str
    type: str
    rotation: int
    color: str
    scale: float
    score: int

# @dataclass
# class SessionState:
#     loots_info_state:LootList = field(default_factory=list)
#     map_id: str = ""
#     player_id: int = 0
#     # players = []
#     players:'PlayersList' = field(default_factory=list)


@dataclass
class SessionInfo:
    map_id: str = ""
    players: PlayerStateList = field(default_factory=list)
    loots_info_state: LootList = field(default_factory=list)

GameState = list[SessionInfo]

@dataclass
class GatheredLootItem:
    id_: int
    type_: int

GatheredLootList = list[GatheredLootItem]

@dataclass
class DogState:
    pos_: Point = field(default_factory=Point)
    dir_: str = ""
    score: int = 0

    idle_time:int = 0
    play_time:int = 0
    cur_road:int  = 0
    bag: GatheredLootList = field(default_factory=list)

@dataclass
class PlayerState:
    id_:int = 0
    name:str = ""
    token: str = ""
    dog: DogState = field(default_factory=DogState)

PlayerStateList = list[PlayerState]

@dataclass
class PlayerRecordItem:
	# id: str
	name: str
	score: int
	play_time: int

@dataclass
class DogSpeed:
    vx: float = 0.0
    vy: float = 0.0

class RoadBoundRect:

    def __init__(self):
        self.min_point = Point()
        self.max_point = Point()

    def point_inside(self, new_pos: Point) -> bool:
        if ((new_pos.x >= self.min_point.x) and (new_pos.x <= self.max_point.x) and
            (new_pos.y >= self.min_point.y) and (new_pos.y <= self.max_point.y)):
            return True

        return False

class DogDirection(str, Enum):
    NORTH = "U"
    SOUTH = "D"
    WEST = "L"
    EAST = "R"
    STOP = ""
