# from dataclasses import dataclass
# from enum import Enum
from models.MapModel import (Point, Map, roads_adjacent,
                             roads_crossed, correct_dog_position_inside_road)
from game.utils.DataTypes import LootInfo, RoadMutualPositionType, LootList, RoadBoundRect, DogDirection, DogSpeed, PlayerState, DogState, GatheredLootItem
from typing import Optional
from game.utils.RandomGenerator import get_random_number
from game_exceptions.Exceptions import DogSpeedException
from game.utils.CollisionDetector import Gatherer

dS = 0.4
millisecondsInSecond = 1000
gathererWidth = 0.6
epsilon = 0.0001

class Dog:
    def __init__(self, map_: Map, default_bag_capacity: int):
        self.bag_capacity_ = map_.bag_capacity if map_.bag_capacity is not None else default_bag_capacity
        self.map_ = map_
        self.roads_ = map_.roads
        self.direction_ = DogDirection.NORTH

        self.speed_ = DogSpeed()
        self.position_ = Point()
        self.gathered_loots_ = []
        self.score_ = 0
        self.current_road_index_ = 0
        self.adjacent_roads_ = [set() for _ in range(len(self.roads_))]
        self.play_time_ = 0
        self.idle_time_ = 0
        self.find_adjacent_roads()

    def set_speed(self, dir_: DogDirection, speed: float) -> None:
        vel_map = {
          DogDirection.EAST: DogSpeed(speed, 0),
          DogDirection.WEST: DogSpeed(-speed, 0),
          DogDirection.SOUTH: DogSpeed(0, speed),
          DogDirection.NORTH: DogSpeed(0, -speed),
          DogDirection.STOP: DogSpeed()}

        find_vel = vel_map.get(dir_)
        if find_vel is None:
            raise DogSpeedException('Invalid dog speed')

        if dir_ != DogDirection.STOP:
            self.direction_ = dir_
        # self.direction_ = dir_
        # self.idle_time_ = 0

        self.speed_ = find_vel
        # self.navigator_.SetDogSpeed

    def spawn_dog_in_map(self, spawn_in_random_point: bool) -> None:
        if spawn_in_random_point is True:
            self.set_start_position_random_road()
        else:
            self.set_start_position_first_road()

    def find_adjacent_roads(self) -> None:
        for i in range(len(self.roads_)):
            for j in range(i+1, len(self.roads_)):
                road_type = RoadMutualPositionType.Parallel

                if roads_adjacent(self.roads_[i], self.roads_[j]):
                    road_type = RoadMutualPositionType.Adjacent
                else:
                    if roads_crossed(self.roads_[i], self.roads_[j]):
                        road_type = RoadMutualPositionType.Crossed

                if road_type != RoadMutualPositionType.Parallel:
                    self.adjacent_roads_[i].add(j) #RoadInfo(j, road_type))
                    self.adjacent_roads_[j].add(i)#RoadInfo(i, road_type))

    def set_start_position_first_road(self) -> None:
        self.current_road_index_ = 0
        start = self.roads_[self.current_road_index_].get_start()
        self.position_ = start

    def set_start_position_random_road(self) -> None:
        self.current_road_index_ = int(get_random_number(0, len(self.roads_)))
        start = self.roads_[self.current_road_index_].get_start()
        end = self.roads_[self.current_road_index_].get_end()

        if self.roads_[self.current_road_index_].is_horizontal() is True:
            if start.x > end.x:
                start, end = end, start
            self.position_ = Point(get_random_number(start.x, end.x), start.y)
        else:
            if start.y > end.y:
                start, end = end, start
            self.position_ = Point(start.x, get_random_number(start.y, end.y))

    def set_direction(self, dir_: DogDirection) -> None:
        self.direction_ = dir_

    def get_current_road_bound_rect(self, road_index: int) -> RoadBoundRect:
        road = self.roads_[road_index]
        x_min = min(road.get_start().x, road.get_end().x)
        x_max = max(road.get_start().x, road.get_end().x)

        y_min = min(road.get_start().y, road.get_end().y)
        y_max = max(road.get_start().y, road.get_end().y)

        bound_rect = RoadBoundRect()
        bound_rect.min_point = Point(x = x_min - dS, y = y_min - dS)
        bound_rect.max_point = Point(x = x_max + dS, y = y_max + dS)
        return bound_rect

    def search_position_inside_adjacent_roads(self, pos: Point) -> Optional[int]:
        for road_index in self.adjacent_roads_[self.current_road_index_]:
            bound_rect = self.get_current_road_bound_rect(road_index)
            if bound_rect.point_inside(pos) is True:
                return road_index

        return None

    def evaluate_new_position(self, delta_time: int) -> Point:
        dt = float(delta_time) / millisecondsInSecond

        return Point(x=self.position_.x + dt * self.speed_.vx, y=self.position_.y + dt * self.speed_.vy)

    def change_position(self, delta_time: int) -> None:
        bound_rect = self.get_current_road_bound_rect(self.current_road_index_)
        new_pos = self.evaluate_new_position(delta_time)
        if bound_rect.point_inside(new_pos):
            self.position_ = new_pos
            return
        else:
            adj_road_index = self.search_position_inside_adjacent_roads(new_pos)
            if adj_road_index is not None:
                self.current_road_index_ = adj_road_index
                self.position_ = new_pos
            else:
                self.position_ = correct_dog_position_inside_road(new_pos, bound_rect)
                self.speed_.vx = 0.0
                self.speed_.vy = 0.0

    def move(self, delta_time: int) -> Optional[Gatherer]:
        # self.play_time_ += delta_time
        if self.direction_ == DogDirection.STOP:
            # self.idle_time_ += delta_time
            return None
        # else:
        #     self.idle_time_ = 0

        start = self.get_position()
        
        self.change_position(delta_time)
        end = self.get_position()

        if ((abs(start.x-end.x) > epsilon) or
            (abs(start.y - end.y) > epsilon)):
            gatherer = Gatherer(Point(start.x, start.y), Point(end.x, end.y), gathererWidth)
            return gatherer

    def get_direction(self) -> DogDirection:
        return self.direction_

    def get_position(self) -> Point:
        return self.position_

    def set_position(self, point: Point) -> None:
        self.position_ = point

    def get_speed(self) -> DogSpeed:
        return self.speed_

    def get_gathered_loot(self) -> LootList:
        return self.gathered_loots_

    def append_gathered_loot(self, loot: LootInfo) -> None:
        self.gathered_loots_.append(loot)

    def get_idle_time(self) -> int:
        return self.idle_time_

    def add_idle_time(self, delta:int) -> None:
        self.idle_time_ += delta

    def set_idle_time(self, time: int):
        self.idle_time_ = time

    def get_road_index(self) -> int:
        return self.current_road_index_

    def set_road_index(self, road_index: int):
        self.current_road_index_ = road_index

    def add_loot(self, loot: LootInfo) -> bool:
        if len(self.gathered_loots_) >= self.bag_capacity_:
            return False

        self.gathered_loots_.append(loot)
        return True

    def pass_loot_to_office(self) -> None:
        loots = self.map_.loots

        for loot in self.gathered_loots_:
            self.score_ += loots[loot.type].score

        self.gathered_loots_.clear()

    def get_score(self) -> int:
        return self.score_

    def set_score(self, score: int) -> None:
        self.score_ += score

    def get_play_time(self) -> int:
        return self.play_time_

    def get_bag_capacity(self):
        return self.bag_capacity_

    def add_play_time(self, delta: int) -> None:
        self.play_time_ += delta

    def set_play_time(self, play_time: int) -> None:
        self.play_time_ = play_time

    def get_state(self) -> DogState:
        bag = list()
        for loot in self.gathered_loots_:
            bag.append(GatheredLootItem(id_= loot.id, type_ = loot.type))

        return DogState(pos_=self.position_, dir_= self.direction_, score=self.score_, idle_time=self.idle_time_,
                        play_time=self.play_time_, cur_road=self.current_road_index_, bag=bag)


class Player:
    # def __init__(self, id_: int, name: str, token: str, map_: Map, default_bag_capacity: int):
    def __init__(self, id_: int, name: str, token: str, dog: Dog):
        self.id_ = id_
        self.name_ = name
        self.token_ = token
        self.dog_ = dog

    def GetToken(self) -> str:
        return self.token_

    def set_token(self, token: str) -> None:
        self.token_ = token

    def GetName(self) -> str:
        return self.name_

    def set_name(self, name: str) -> None:
        self.name_ = name

    def get_id(self) -> int:
        return self.id_

    def set_id(self, id_: int) ->None:
        self.id_ = id_

    def GetDog(self) -> Dog:
        return self.dog_

    def get_state(self) -> PlayerState:
        return PlayerState(id_=self.id_, name=self.name_, token=self.token_, dog=self.dog_.get_state())

PlayersList = list[Player]
