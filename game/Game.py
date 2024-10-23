import traceback

from models.MapModel import Map
from typing import Optional, Any, Coroutine
from game.utils.GameSession import GameSession
from game.utils.Dog import Dog, Player
from game.utils.DataTypes import PlayerRecordItem, LootList, DogDirection, LootInfo, PlayerState
from game.MapParser import MapStorage, LootConfig
from game_exceptions.Exceptions import (PlayerAbsentException, InvalidSessionException,
                                        EmptyNameException, MapNotFoundException)
from traceback import format_exc, print_exc
import logging
from game.utils.GameTimer import SaveDataCoroutineRunner
from models.ConcreteRepository import (ConcreteRepository, convert_to_db_representation,
                                       convert_from_db_representation)

from game.utils.FileUtils import write_json
import game.utils.ModelSerialization
from game.utils.ModelSerialization import GameState
from models.ConcreteRepository import ConcreteRepository, create_database
from game.utils.Converter import convert_future
from pyinstrument import Profiler

logger = logging.getLogger(__name__)

# from game.utils.ModelSerialization import SerializeSessions

LootParameters = (float, float)
Maps = dict[str, Map]
PlayerAuthInfo = (str, int)
MapIdToIndex = dict[str, int]
PlayersList = list[Player]

config_path: str = "/data/config.json"

class Game:

    def __init__(self, storage: MapStorage, spawn_in_random_points : bool, repository: ConcreteRepository, exception_coro: Coroutine):
        self.storage_ = storage
        # self.config_ = config
        # self.maps_ = {}
        self.sessions_ = []
        self.default_dog_speed_ = 0.0
        self.dog_retirement_time_ = 60*1000.0
        self.tick_period_ = -1
        self.spawn_in_random_points_ = spawn_in_random_points
        self.loot_period_ = 0.0
        self.loot_probability_ = 0.0
        self.save_period = 0
        self.time_without_saving_ = 0
        self.repository_ = repository
        self.data_saver_ = SaveDataCoroutineRunner()
        self.exception_handler_ = exception_coro
        # self.default_bag_capacity_ = 0

    def find_map(self, id_: Map.id) -> Optional[Map]:
        # return self.maps_.get(id_)
        return self.storage_.get_map(id_)

    def find_all_players_for_auth_info(self, auth_token: str) -> PlayersList:
        session = self.__get_session_for_token(auth_token)
        if session is None:
            return []

        return session.get_all_players()

    def get_loots_for_auth_info(self, auth_token: str) -> LootList:
        session = self.__get_session_for_token(auth_token)
        if session is None:
            return []

        return session.get_loots_info()

    def GetPlayerWithAuthToken(self, auth_token: str) -> Optional[Player]:
        res = filter(lambda session: session.HasPlayerWithAuthToken(auth_token) is True, self.sessions_)
        sessions = list(res)

        if len(sessions) == 0:
            raise PlayerAbsentException('Unknown token')

        return sessions[0].GetPlayerWithAuthToken(auth_token)

    def has_session_with_auth_info(self, auth_token: str) -> bool:
        res = filter(lambda session: session.HasPlayerWithAuthToken(auth_token) == True, self.sessions_)
        sessions = list(res)
        if len(sessions) == 0:
            return False

        return True

    def get_session_with_auth_info(self, auth_token: str) -> Optional[GameSession]:
        res = filter(lambda session: session.HasPlayerWithAuthToken(auth_token) == True, self.sessions_)
        sessions = list(res)

        if len(sessions) == 0:
            raise InvalidSessionException('Session not found')

        return sessions[0]

    def add_player(self, map_id: str, player_name: str) -> PlayerAuthInfo:
        map_to_add = self.find_map(map_id)

        if len(player_name) == 0:
            raise EmptyNameException('Empty player name')

        if map_to_add is None:
            raise MapNotFoundException('Specified map not found')

        session = self.__find_session(map_id)
        if session is None:
            loot_period, loot_probability = self.get_loot_parameters()
            session = GameSession(map_id, loot_period, loot_probability)
            self.sessions_.append(session)

        player = session.add_player(player_name, map_to_add,
                                    self.spawn_in_random_points_, self.storage_.get_default_bag_capacity())
        # player.GetDog().SpawnDogInMap(self.GetSpawnInRandomPoint())
        return player.GetToken(), player.get_id()

    def get_default_dog_speed(self) -> float:
        return self.storage_.get_default_dog_speed()
        # return self.default_dog_speed_

    def MoveDogs(self, delta_time: int) -> None:
        for session in self.sessions_:
            session.MoveDogs(delta_time)

    def GenerateLoot(self, delta_time: int) -> None:
        for session in self.sessions_:
            map_name = session.GetMap()
            cur_map = self.find_map(map_name)
            if cur_map is not None:
                session.GenerateLoot(delta_time, cur_map)

    def set_tick_period(self, period: int) -> None:
        self.tick_period_ = period

    def get_tick_period(self) -> int:
        return self.tick_period_

    def set_loot_parameters(self, loot: LootConfig) -> None:
        self.loot_period_ = loot["period"]
        self.loot_probability_ = loot["probability"]

    def get_loot_parameters(self) -> LootParameters:
        return self.loot_period_, self.loot_probability_

    def __find_session(self, map_name: str) -> Optional[GameSession]:
        res = filter(lambda session: session.GetMap() == map_name, self.sessions_)
        sessions = list(res)
        if len(sessions) > 0:
            return sessions[0]

        return None

    def __get_session_for_token(self, auth_token: str) -> Optional[GameSession]:
        res = filter(lambda session: session.HasPlayerWithAuthToken(auth_token) is True, self.sessions_)
        sessions = list(res)
        if len(sessions) > 0:
            return sessions[0]

        return None

    def timer_handler(self) -> None:
        try:
            period = self.get_tick_period()

            self.GenerateLoot(period)
            self.MoveDogs(period)

            self.data_saver_.start(self.serialize_sessions, period)
            self.data_saver_.start(self.handle_retired_players)

        except Exception as ex:
            logger.exception(print_exc())

    def set_save_period(self, period: int) -> None:
        self.save_period = period

    def create_game_state(self) -> GameState:
        if not self.save_period:
            return []

        session_list = []
        for session in self.sessions_:
            session_list.append(session.get_session_state())

        return session_list

    async def serialize_sessions(self, interval: int) -> None:
        self.time_without_saving_ += interval
        if self.time_without_saving_ < self.save_period:
            return

        state = self.create_game_state()
        if not state:
            return
        serialized_state = game.utils.ModelSerialization.save_sessions_states(state)
        if serialized_state:
            await write_json("/sessions_state.tmp", serialized_state)

        self.time_without_saving_ = 0

    def init_dog(self, dog: Dog, player_state: PlayerState) -> None:
        dog.set_position(player_state.dog.pos_)
        dog.set_direction(DogDirection(player_state.dog.dir_))
        dog.set_score(player_state.dog.score)
        dog.set_idle_time(player_state.dog.idle_time)
        dog.set_play_time(player_state.dog.play_time)
        dog.set_road_index(player_state.dog.cur_road)

        for item in player_state.dog.bag:
            dog.append_gathered_loot(LootInfo(id=item.id_, type=item.type_, x=0, y=0))


    def restore_sessions(self, session_content):
        self.sessions_.clear()
        for state in game.utils.ModelSerialization.restore_sessions_states(session_content):
            loot_period, loot_probability = self.get_loot_parameters()
            session = GameSession(state.map_id, loot_period, loot_probability)

            session.set_loot_list(state.loots_info_state)
            for player_state in state.players:
                map_to_add = self.find_map(state.map_id)
                player = session.add_player(player_state.name, map_to_add,
                                            self.spawn_in_random_points_, self.storage_.get_default_bag_capacity())
                player.set_id(player_state.id_)
                # player.set_name(player_state.name)
                player.set_token(player_state.token)
                dog = player.GetDog()
                self.init_dog(dog, player_state)

            self.sessions_.append(session)


    def find_expired_players(self) -> list[Player]:
        # dog_retirement_time = 60 * 1000

        result = []
        for session in self.sessions_:
            for player in session.get_all_players():
                idle_time = player.GetDog().get_idle_time()
                if idle_time >= self.dog_retirement_time_:
                    result.append(player)

        return result

    async def save_expired_players(self, players: list[Player]) -> None:
        # players = self.find_expired_players()
        retired = []
        for player in players:
            dog = player.GetDog()
            retired.append(PlayerRecordItem(player.GetName(), dog.get_score(), dog.get_play_time()))

        await self.repository_.save_retired(convert_to_db_representation(retired))

    def delete_expired_players(self, players: list[Player]) -> None:
        for player in players:
            for session in self.sessions_:
                candidate = session.GetPlayerWithAuthToken(player.GetToken())
                if candidate:
                    session.delete_player(candidate)
                    break

    def delete_empty_sessions(self) -> None:
        session_list = []

        for session in self.sessions_:
            if session.get_all_players().empty():
                session_list.append(session)

        for session in session_list:
            self.sessions_.remove(session)

    async def handle_retired_players(self) -> None:
        expired_players = self.find_expired_players()
        if not expired_players:
            return

        await self.save_expired_players(expired_players)
        self.delete_expired_players(expired_players)
        self.delete_empty_sessions()

    async def get_retired_players(self, start: int, max_items: int) -> list[PlayerRecordItem]:
        try:
            # res = await asyncio.wrap_future(self.data_saver_.start(self.repository_.get_retired, start, max_items))
            res = await convert_future(self.data_saver_.start(self.repository_.get_retired, start, max_items))
            return convert_from_db_representation(res)
        except Exception as ex:
            print(ex.args)

    def set_dog_retirement_time(self, period: float) -> None:
        self.dog_retirement_time_ = period

    def set_default_dog_speed(self, speed: float) -> None:
        self.default_dog_speed_ = speed

def create_game(config_content: Any, repository: ConcreteRepository, exception_coro: Coroutine) -> Game:
    storage = MapStorage()
    storage.parse_maps(config_content)
    game = Game(storage, False, repository, exception_coro)

    game.data_saver_.start(create_database, 'postgres', 'records')
    game.data_saver_.start(game.repository_.create_table)

    game.set_default_dog_speed(storage.get_default_dog_speed())
    game.set_dog_retirement_time(storage.get_dog_retirement_time()*1000)
    game.set_loot_parameters(storage.get_loot_config())
    game.set_save_period(15000)
    game.set_tick_period(100)

    # game.SetDefaultBagCapacity(storage.getDefaultBagCapacity())

    return game
