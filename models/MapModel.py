# from __future__ import annotations
# from dataclasses import dataclass
from game.utils.DataTypes import Point, Offset, RoadBoundRect, RoadType, Coord, Loot, Office
from enum import Enum
from game_exceptions.Exceptions import UnknownRoadOrientation

class Road:
    # start: Point
    # end: Point
    def __init__(self, road_type: RoadType, start: Point, end: Coord):
        if road_type is RoadType.HORIZONTAL:
            self.start = start
            self.end = Point(end, start.y)
        elif road_type is RoadType.VERTICAL:
            self.start = start
            self.end = Point(start.x, end)
        else:
            raise UnknownRoadOrientation("unknown road orientation")

    def is_horizontal(self) -> bool:
        return self.start.y == self.end.y

    def is_vertical(self) -> bool:
        return self.start.x == self.end.x

    def get_start(self) -> Point:
        return self.start

    def get_end(self) -> Point:
        return self.end

Roads = list[Road]

class Map:
    # Id = str
    # Roads = list[Road]
    # # Offices = dict[str, Office]
    # Loots = list[Loot]

    def __init__(self, id_: str, name: str):
        self.__id = id_
        self.__name = name
        self.__roads = []
        self.__offices = []
        self.__loots = []
        self.__dog_speed = 0.0
        self.__bag_capacity = 1

    @property
    def id(self) -> str:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def roads(self) -> Roads:
        return self.__roads

    def get_num_roads(self) -> int:
        return len(self.__roads)

    @property
    def offices(self) -> list:
        return self.__offices

    @property
    def loots(self) -> list:
        return self.__loots

    def add_road(self, road: Road) -> None:
        self.__roads.append(road)

    def add_office(self, office: Office) -> None:
        self.__offices.append(office)

    def add_loot(self, loot: Loot) -> None:
        self.__loots.append(loot)

    def get_num_loots(self) -> int:
        return len(self.__loots)

    def set_dog_speed(self, speed: float) -> None:
        self.__dog_speed = speed

    @property
    def dog_speed(self) -> float:
        return self.__dog_speed

    def set_bag_capacity(self, capacity: int) -> None:
        self.__bag_capacity = capacity

    @property
    def bag_capacity(self) -> int:
        return self.__bag_capacity

def correct_dog_position_inside_road(pos: Point, bound_rect: RoadBoundRect) -> Point:
    if pos.x < bound_rect.min_point.x:
        pos.x = bound_rect.min_point.x

    if pos.x > bound_rect.max_point.x:
        pos.x = bound_rect.max_point.x

    if pos.y < bound_rect.min_point.y:
        pos.y = bound_rect.min_point.y

    if pos.y > bound_rect.max_point.y:
        pos.y = bound_rect.max_point.y

    return pos

def roads_crossed(road1: Road, road2: Road) -> bool:
    if (road1.is_horizontal() and road2.is_vertical()) or (road1.is_vertical() and road2.is_horizontal()):
        first_start = road1.get_start()
        second_start = road2.get_start()
        second_end = road2.get_end()

        if road1.is_horizontal():
            if (((second_start.y < first_start.y) and (second_end.y < first_start.y)) or
                ((second_start.y > first_start.y) and (second_end.y > first_start.y))):
                return False
        else:
            if road1.is_vertical():
                if (((second_start.x < first_start.x) and (second_end.x < first_start.x)) or
                    ((second_start.x > first_start.x) and (second_end.x > first_start.x))):
                    return False

        return True

    return False

def roads_adjacent(road1: Road, road2: Road) -> bool:
    if (road1.is_horizontal() and road2.is_horizontal()) or (road1.is_vertical() and road2.is_vertical()):
        first_start = road1.get_start()
        first_end = road1.get_end()

        second_start = road2.get_start()
        second_end = road2.get_end()

        if ((first_start == second_start) or (first_start == second_end) or
            (first_end == second_start) or (first_end == second_end)):
            return True

    return False