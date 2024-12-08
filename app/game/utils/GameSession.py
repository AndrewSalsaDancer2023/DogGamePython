from game.utils.Dog import Dog
from models.MapModel import Map
from game.utils.DataTypes import LootList, LootInfo, Point
from game.LootGenerator import LootGenerator
from game.utils.CollisionDetector import Gatherer, ItemGatherer, find_gather_events
from game_exceptions.Exceptions import PlayerAbsentException, LootNotSpecifiedException, RoadNotSpecifiedException
from game.utils.RandomGenerator import get_random_number
from game.utils.CollisionDetector import Item, ItemType, ItemList
from game.utils.DataTypes import SessionInfo
from game.utils.Dog import Player, PlayersList
from typing import Optional
import uuid

baseWidth = 0.5
lootWidth = 0.0


class GameSession:

	def __init__(self, map_id: str, loot_period: float, loot_probability: float):
		self.map_id_ = map_id
		self.lootGen_ = None
		self.init_loot_generator(loot_period, loot_probability)

		self.players_ = []
		self.loots_info_ = []
		self.player_id = 0
		self.map_ = None
		self.loot_id_ = 0

	def get_session_state(self) -> SessionInfo:
		info = SessionInfo()
		info.map_id = self.map_id_
		info.loots_info_state = self.loots_info_
		for player in self.players_:
			info.players.append(player.get_state())

		return info


	def init_loot_generator(self, loot_period: float, loot_probability: float) -> None:
		duration = loot_period * 1000
		self.lootGen_ = LootGenerator(int(duration), loot_probability)

	def add_player(self, player_name: str, player_map: Map, spawn_dog_in_random_point: bool, default_bag_capacity: int) -> Player:
		self.map_ = player_map
		iterator = filter(lambda plr: plr.GetName() == player_name, self.players_)
		player_list = list(iterator)
		if len(player_list) > 0:
			return player_list[0]

		token = uuid.uuid4()
		dog = Dog(self.map_, default_bag_capacity)
		player = Player(self.player_id, player_name, str(token), dog)

		self.players_.append(player)
		self.player_id += 1

		return player

	def GetMap(self) -> str:
		return self.map_id_


	def HasPlayerWithAuthToken(self, auth_token: str) -> bool:
		iterator = filter(lambda player: player.GetToken() == auth_token, self.players_)
		player_list = list(iterator)
		if len(player_list) > 0:
			return True

		return False

	def get_all_players(self) -> PlayersList:
		return self.players_

	def GetPlayerWithAuthToken(self, auth_token: str) -> Optional[Player]:
		iterator = filter(lambda player: player.GetToken() == auth_token, self.players_)
		player_list = list(iterator)
		if len(player_list) > 0:
			return player_list[0]

		return None

	def delete_player(self, player: Player) -> None:
		self.players_.remove(player)

	def MoveDogs(self, delta_time: int) -> None:
		for player in self.players_:
			dog = player.GetDog()
			dog.add_play_time(delta_time)

			gatherer = dog.move(delta_time)
			if gatherer is None:
				dog.add_idle_time(delta_time)
				return

			dog.set_idle_time(0)

			items = self.get_gathered_items(gatherer, self.loots_info_, self.map_)
			self.add_loot_to_dog(player.GetDog(), self.loots_info_, items)

	def GetNumPlayers(self) -> int:
		return len(self.players_)

	def get_loots_info(self) -> LootList:
		return self.loots_info_

	def set_loot_list(self, loot: LootList):
		self.loots_info_ = loot
		self.loot_id_ += len(loot)


	def GenerateLoot(self, deltaTime: int, map_: Map) -> None:
		num_loot_to_generate = self.lootGen_.Generate(deltaTime, len(self.loots_info_), len(self.players_))

		while num_loot_to_generate > 0:
			self.loots_info_.append(self.generate_loot_info(map_))
			num_loot_to_generate = - 1

	def get_loot_position(self, start: Point, end: Point, horizontal_road: bool) -> (float, float):
		if horizontal_road is True:
			if start.x > end.x:
				start, end = end, start

			x = get_random_number(start.x, end.x)
			y = start.y
			return (x, y)

		if start.y > end.y:
			start, end = end, start

		x = start.x
		y = get_random_number(start.y, end.y)
		return (x, y)

	def generate_loot_info(self, map_: Map) -> LootInfo:
		roads = map_.roads
		num_loots = map_.get_num_loots()
		if num_loots == 0:
			raise LootNotSpecifiedException("No loot specified for the map!")

		loot_type = int(get_random_number(0, num_loots))

		num_roads = map_.get_num_roads()
		if num_roads == 0:
			raise RoadNotSpecifiedException("No roads specified for the map!")

		road_index = int(get_random_number(0, num_roads))

		start = roads[road_index].get_start()
		end = roads[road_index].get_end()

		x, y = self.get_loot_position(start, end, roads[road_index].is_horizontal())

		loot_info = LootInfo(self.loot_id_, loot_type, x, y)
		self.loot_id_ += 1
		return loot_info

	def get_gathered_items(self, gatherer: Gatherer, loots: LootList, map_: Map) -> ItemList:
		items = []
		for cur_loot in loots:
			item = Item(cur_loot.id, Point(cur_loot.x, cur_loot.y), lootWidth)
			items.append(item)

		for office in map_.offices:
			item = Item(0, office.position, baseWidth, ItemType.Office)
			items.append(item)

		item_gath = ItemGatherer(items, [gatherer])
		ev = find_gather_events(item_gath)

		result = []

		for i in range(len(ev)):
			result.append(item_gath.get_item(ev[i].item_id))

		return result

	def add_loot_to_dog(self, dog: Dog, loots: LootList, items: ItemList) -> None:
		for item in items:
			if item.item_type == ItemType.Office:
				dog.pass_loot_to_office()
			else:
				res = filter(lambda elem: elem.id == item.id_, loots)
				filtered = list(res)

				if len(filtered) == 0:
					continue

				if dog.add_loot(filtered[0]):
					loots.remove(filtered[0])
