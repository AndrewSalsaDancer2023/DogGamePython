from pydantic import BaseModel
from game.utils.Dog import DogDirection

class JoinModel(BaseModel):
    userName: str
    mapId: str

class MoveModel(BaseModel):
    move: DogDirection

class TickModel(BaseModel):
    timeDelta: int

class RecordModel(BaseModel):
    start: int
    maxItems: int
