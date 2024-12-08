
from game.utils.DataTypes import (LootList, Point, LootInfo, GameState, GatheredLootItem,
								  DogState, PlayerState, GatheredLootList, SessionInfo)

from game.utils.Dog import Dog, DogDirection, Player, PlayersList
from typing import Any

def serialize_dog_bag(loots: GatheredLootList) -> list:
	bag_ar = list()
	for cur_loot in loots:
		bag_ar.append({"id": cur_loot.id_, "type": cur_loot.type_})

	return bag_ar

def serialize_player_dog_bag(loots: LootList) -> list:
	bag_ar = list()
	for cur_loot in loots:
		bag_ar.append({"id": cur_loot.id, "type": cur_loot.type})

	return bag_ar

def deserialize_dog_bag(bag: Any) -> GatheredLootList:
	bag_ar = list()
	for bag_item in bag:
		item = GatheredLootItem(int(bag_item["id"]), int(bag_item["type"]))
		bag_ar.append(item)

	return bag_ar

def serialize_loot(loot: LootInfo) -> dict:
	result = dict()
	result["id"] = loot.id
	result["type"] = loot.type
	result["pos"] = [loot.x, loot.y]
	return result

def deserialize_loot(json: Any) -> LootInfo:
	loot_info = LootInfo()
	loot_info.id = int(json["id"])
	loot_info.type = int(json["type"])
	loot_info.x = [float(json["pos"][0]), float(json["pos"][1])] #float(json["pos"][0])
	# loot_info.y = float(json["pos"][1]) #float(json["pos"][1])

	return loot_info

# def deserialize_loot_list(loots: Any) -> LootList:
# 	loot_list = LootList()
#
# 	for loot in loots:
# 		loot_list.append(deserialize_loot(loot))
#
# 	return loot_list

def serialize_player(player: PlayerState) -> dict:
	player_object = dict()
	player_object["id"] = player.id_
	player_object["name"] = player.name
	player_object["token"] = player.token

	player_object["dog"] = serialize_dog(player.dog)

	return player_object

def deserialize_player(player_object: Any) -> PlayerState:
	id_ = int(player_object["id"])
	name = str(player_object["name"])
	token = str(player_object["token"])
	dog_state = deserialize_dog(player_object["dog"])
	return PlayerState(id_, name, token, dog_state)

def deserialize_dog(dog_object: Any) -> DogState:

	pos = Point(x=dog_object["pos"][0], y=dog_object["pos"][1])
	dir_ = DogDirection(dog_object["dir"])
	score = int(dog_object["score"])

	idle_time = int(dog_object["idle-time"])
	play_time = int(dog_object["play-time"])
	cur_road = int(dog_object["road"])
	bag = deserialize_dog_bag(dog_object["bag"])

	return DogState(pos, dir_, score, idle_time, play_time, cur_road, bag)

def serialize_dog(dog: DogState) -> dict:
	dog_object = dict()
	dog_object["pos"] = [dog.pos_.x, dog.pos_.y]
	dog_object["dir"] = dog.dir_
	dog_object["score"] = dog.score

	dog_object["idle-time"] = dog.idle_time
	dog_object["play-time"] = dog.play_time
	dog_object["road"] = dog.cur_road

	dog_object["bag"] = serialize_dog_bag(dog.bag)
	return dog_object

def serialize_player_dog(dog: Dog) -> dict:
	dog_object = dict()
	pos = dog.get_position()
	dog_object["pos"] = [pos.x, pos.y]
	dog_object["dir"] = dog.get_direction()
	dog_object["score"] = dog.get_score()
	speed = dog.get_speed()
	dog_object["speed"] = [speed.vx, speed.vy]

	dog_object["idle-time"] = dog.get_idle_time()
	dog_object["play-time"] = dog.get_play_time()
	dog_object["road"] = dog.get_road_index()

	dog_object["bag"] = serialize_player_dog_bag(dog.get_gathered_loot())
	return dog_object

def serialize_dogs(players: PlayersList) -> dict:
	players_object = dict()

	for player in players:
		dog = player.GetDog()
		dog_object = serialize_player_dog(dog)
		players_object[str(player.get_id())] = dog_object

	return players_object

def serialize_loots(loots: LootList) -> dict:
	loots_object = dict()

	for i in range(len(loots)):
		loot_object = dict()
		loot_object["pos"] = [loots[i].x, loots[i].y]
		loot_object["type"] = loots[i].type

		loots_object[str(i)] = loot_object

	return loots_object

def save_sessions_states(game_state: GameState) -> list:
	result = list()
	for state in game_state:
		items = dict()
		items["map_id"] = state.map_id
		loots = []
		for item in state.loots_info_state:
			loots.append(serialize_loot(item))

		items["loot"] = loots

		players = []
		for player in state.players:
			players.append(serialize_player(player))

		items["players"] = players

		result.append(items)

	return result

def restore_sessions_states(config_content: Any) -> GameState:
	states = []
	for session_state in config_content:
		state_ = SessionInfo()

		state_.map_id = str(session_state["map_id"])

		for loot in session_state["loot"]:
			state_.loots_info_state.append(deserialize_loot(loot))

		for player_ in session_state["players"]:
			state_.players.append(deserialize_player(player_))
			# else:
			# 	raise AbsentMapException()
		states.append(state_)

	return states