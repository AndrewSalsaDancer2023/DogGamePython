# from dataclasses import dataclass
import abc
from game.utils.DataTypes import PlayerRecordItem

class IAbstractRepository(abc.ABC):
    @abc.abstractmethod
    async def save_retired(self, players: list[PlayerRecordItem]) -> None:
        pass

    @abc.abstractmethod
    async def get_retired(self, start: int, max_items: int) -> list[PlayerRecordItem]:
        pass

    async def create_database(self) -> None:
        pass

    @abc.abstractmethod
    async def create_table(self) -> None:
        pass
