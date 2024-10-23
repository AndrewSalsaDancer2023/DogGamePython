from enum import Enum
from models.MapModel import Point
from dataclasses import dataclass
import abc

class ItemType(int, Enum):
    Loot = 1
    Office = 2

class CollectionResult:
    def __init__(self, sq_distance: float, proj_ratio: float):
        self.sq_distance = sq_distance  #квадрат расстояния до точки
        self.proj_ratio = proj_ratio  #доля пройденного отрезка

    def is_collected(self, collect_radius: float) -> bool:
        return (self.proj_ratio >= 0 and self.proj_ratio <= 1) and (self.sq_distance <= collect_radius * collect_radius)


class Item:
    def __init__(self, id_: int, pos: Point, width: float, type_: ItemType = ItemType.Loot):
        self.id_ = id_
        self.item_type = type_
        self.position = pos
        self.width = width

ItemList = list[Item]

@dataclass
class Gatherer:
    start_pos: Point
    end_pos: Point
    width: float

@dataclass
class GatheringEvent:
    item_id: int = 0
    gatherer_id: int = 0
    sq_distance: float = 0.0
    time: float = 0.0

class ItemGathererProvider(abc.ABC):
    @abc.abstractmethod
    def items_count(self) -> int: pass

    @abc.abstractmethod
    def get_item(self, idx: int) -> Item: pass

    @abc.abstractmethod
    def gatherers_count(self) -> int: pass

    @abc.abstractmethod
    def get_gatherer(self, idx: int) -> Gatherer: pass

class ItemGatherer(ItemGathererProvider):
    def __init__(self, items: list[Item], gatherers: list[Gatherer]):
        self.items_ = items
        self.gatherers_ = gatherers

    def items_count(self) -> int:
        return len(self.items_)

    def get_item(self, idx: int) -> Item:
        return self.items_[idx]

    def gatherers_count(self) -> int:
        return len(self.gatherers_)

    def get_gatherer(self, idx: int) -> Gatherer:
        return self.gatherers_[idx]

# Движемся из точки a в точку b и пытаемся подобрать точку c.
def TryCollectPoint(a: Point, b: Point, c: Point) -> CollectionResult:
    # Проверим, что перемещение ненулевое.
    # Тут приходится использовать строгое равенство, а не приближённое,
    # пскольку при сборе заказов придётся учитывать перемещение даже на небольшое расстояние.
    assert (b.x != a.x or b.y != a.y)
    u_x = c.x - a.x
    u_y = c.y - a.y
    v_x = b.x - a.x
    v_y = b.y - a.y
    u_dot_v = u_x * v_x + u_y * v_y
    u_len2 = u_x * u_x + u_y * u_y
    v_len2 = v_x * v_x + v_y * v_y
    proj_ratio = u_dot_v / v_len2
    sq_distance = u_len2 - (u_dot_v * u_dot_v) / v_len2

    return CollectionResult(sq_distance, proj_ratio)

def find_gather_events(provider: ItemGathererProvider) -> list[GatheringEvent]:
    events = []
    epsilon = 1e-10
    for i in range(provider.gatherers_count()):
        gatherer = provider.get_gatherer(i)

        if ((abs(gatherer.start_pos.x - gatherer.end_pos.x) <= epsilon) and
                (abs(gatherer.start_pos.y - gatherer.end_pos.y) <= epsilon)):
            continue

        for j in range(provider.items_count()):
            item = provider.get_item(j)
            result = TryCollectPoint(gatherer.start_pos, gatherer.end_pos, item.position)

            if result.is_collected(gatherer.width + item.width) is True:
                evt = GatheringEvent(j, i, result.sq_distance, result.proj_ratio)
                events.append(evt)

    events.sort(key= lambda event: event.time)
    return events
