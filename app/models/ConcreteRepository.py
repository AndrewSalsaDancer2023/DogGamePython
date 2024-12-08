from models.AbstractRepository import IAbstractRepository
from game.utils.DataTypes import PlayerRecordItem
from sqlalchemy import Column, Integer, String, desc
from sqlalchemy.orm import declarative_base

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker
import asyncpg
from asyncpg import DuplicateDatabaseError
import threading

Base = declarative_base()
# repository_url_default = 'postgresql+asyncpg://postgres:postgres@localhost/template1'
repository_url_default = 'postgresql+asyncpg://postgres:postgres@db/postgres'
template_url = 'postgresql://postgres:postgres@localhost/template1'

class Player(Base):
    __tablename__ = 'records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable = False)
    score = Column(Integer, index=True, nullable = False)
    play_time_ms = Column(Integer, nullable = False)

    def __repr__(self):
        return f'Player name: {self.name} score is {self.score}, playtime {self.play_time_ms}'

def convert_to_db_representation(items: list[PlayerRecordItem]) -> list:
    players = []
    for item in items:
        players.append(Player(name=item.name, score=item.score, play_time_ms=item.play_time))

    return players

def convert_from_db_representation(items: list[tuple]) ->list[PlayerRecordItem]:
    players = []
    for item in items:
        players.append(PlayerRecordItem(name=item[0], score=item[1], play_time=item[2]))

    return players

async def create_database(user: str, database: str) -> None:
    try:
        conn = await asyncpg.connect(template_url)
        await conn.execute(f'CREATE DATABASE "{database}" OWNER "{user}";')
        await conn.close()
    except DuplicateDatabaseError:
        pass #this exception tells us that database already created
    # except Exception as ex:
    #     print(ex.args)

class ConcreteRepository(IAbstractRepository):
    def __init__(self, repository_url: str = repository_url_default):
        self.engine = create_async_engine(repository_url)
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False)
        self.lock = threading.Lock()

    async def dispose_repository(self):
        await self.engine.dispose()

    async def save_retired(self, players: list[Player]) -> None:
        try:
            # self.lock.acquire()
            async with self.async_session() as session:
                async with session.begin():
                    session.add_all(players)
            await session.commit()
        except Exception as ex:
            print(ex.args)
        # finally:
        #     pass
            # self.lock.release()

    async def get_retired(self, start: int, max_items: int) -> list[tuple]:
        try:
            # self.lock.acquire()
            async with self.async_session() as session:
                stmt = select(Player).order_by(desc(Player.score)).limit(max_items).offset(start)
                select_result = await session.execute(stmt)
                result = []
                for record in select_result.scalars():
                    result.append((record.name, record.score, record.play_time_ms))

        except Exception as ex:
            print(ex.args)
        finally:
            # self.lock.release()
            return result

    async def create_table(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)



