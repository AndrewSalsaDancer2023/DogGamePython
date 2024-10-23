from models.MapModel import Map, Road, Office, Offset, Loot, RoadType, Point
from typing import Any, Optional
import logging

speedKey = "dogSpeed"
defaultDogSpeedKey = "defaultDogSpeed"
lootConfigKey = "lootGeneratorConfig"
default_Dog_Retirement = "dogRetirementTime"
default_bag_capacity = "defaultBagCapacity"

x = "x"
y = "y"
w = "w"
h = "h"
id_ = "id"
offsetX = "offsetX"
offsetY = "offsetY"

x0 = "x0"
y0 = "y0"
x1 = "x1"
y1 = "y1"
timeDelta = "timeDelta"
userName = "userName"
mapId = "mapId"

name = "name"
file = "file"
type = "type"
rotation = "rotation"
color = "color"
scale = "scale"
value = "value"
dog_Speed = "dogSpeed"
bag_Capacity = "bagCapacity"
roads_key = "roads"
buildings_key = "buildings"
offices_key = "offices"
lootTypes = "lootTypes"
default_Dog_Speed = "defaultDogSpeed"
lootGeneratorConfig = "lootGeneratorConfig"
probability = "probability"
bagCapacityDefault = "defaultBagCapacity"
maps = "maps"
move_key = "move"
period = "period"
directionRight = "R"
directionLeft = "L"
directionDown = "D"
directionUp = "U"
periodConfigKey = "period"
probabilityConfigKey = "probability"

logger = logging.getLogger(__name__)
Maps = dict[str, Map]
LootConfig = dict[str, float]

class MapStorage:
    def __init__(self):
        self.maps = {}
        self.loot_config = {}
        self.defaultDogRetirementTime = 0.0
        self.defaultDogSpeed = 1.0
        self.defaultBagCapacity = 3

    def parse_maps(self, config_content: Any) -> None: #config: ConfigFile):
        if defaultDogSpeedKey in config_content.keys():
            self.defaultDogSpeed = float(config_content[defaultDogSpeedKey])

        if lootConfigKey in config_content.keys():
            loot_config = config_content[lootConfigKey]
            self.loot_config[periodConfigKey] = float(loot_config[periodConfigKey])
            self.loot_config[probabilityConfigKey] = float(loot_config[probabilityConfigKey])

        if default_Dog_Retirement in config_content.keys():
            self.defaultDogRetirementTime = float(config_content[default_Dog_Retirement])

        if default_bag_capacity in config_content.keys():
            self.defaultBagCapacity = int(config_content[default_bag_capacity])

        try:
            for item in config_content["maps"]:
                map_name = item["id"]
                self.maps[map_name]= self.parse_map(item)
        # except:
        #     logger.exception(f'exception during parsing : {map_name}')
        except Exception as ex:
            print( ex.args)

    def get_map(self, map_name: str) -> Optional[Map]:
        return self.maps.get(map_name)

    def parse_road(self, road_repr: Any) -> Road:
        if road_repr.get("x1") is not None:
            road = Road(RoadType.HORIZONTAL, Point(float(road_repr[x0]), float(road_repr[y0])), float(road_repr[x1]))
            return road

        road = Road(RoadType.VERTICAL, Point(float(road_repr[x0]), float(road_repr[y0])), float(road_repr[y1]))
        return road

    def parse_office(self, office_repr: Any) -> Office:
        office = Office(str(office_repr[id_]), Point(float(office_repr[x]), float(office_repr[y])),
                         Offset(float(office_repr[offsetX]), float(office_repr[offsetY])))
        return office

    def parse_loot(self, loot_repr: Any) -> Loot:
        rot = int(loot_repr[rotation]) if loot_repr.get(rotation) else -1
        clr = str(loot_repr[color]) if loot_repr.get(color) else ""
        scl = float(loot_repr[scale]) if loot_repr.get(scale) else 1.0
        val = int(loot_repr[value]) if loot_repr.get(value) else 0

        loot = Loot(loot_repr[name], loot_repr[file], loot_repr[type], rot, clr, scl, val)
        return loot

    def parse_map(self, map_representation: Any) -> Map:
        id_val = str(map_representation[id_])
        name_val = str(map_representation[name])

        map_ = Map(id_val, name_val)

        if map_representation.get(dog_Speed) is not None:
            dog_speed = float(map_representation[dog_Speed])
            map_.set_dog_speed(dog_speed)

        if map_representation.get(bag_Capacity) is not None:
            bag_capacity = int(map_representation[bag_Capacity])
            map_.set_bag_capacity(bag_capacity)

        for road_repr in map_representation[roads_key]:
            road = self.parse_road(road_repr)
            map_.add_road(road)

        for office_repr in map_representation[offices_key]:
            office = self.parse_office(office_repr)
            map_.add_office(office)

        for loot_repr in map_representation[lootTypes]:
            loot = self.parse_loot(loot_repr)
            map_.add_loot(loot)

        return map_

    def get_dog_retirement_time(self) -> float:
        return self.defaultDogRetirementTime

    def get_default_bag_capacity(self) -> int:
        return self.defaultBagCapacity

    def get_default_dog_speed(self) ->float:
        return self.defaultDogSpeed

    def get_loot_config(self) -> LootConfig:
        return self.loot_config
