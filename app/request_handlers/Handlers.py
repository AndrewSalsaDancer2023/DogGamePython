import asyncio
# from cgitb import reset

from models.ReqModel import JoinModel
from game.Game import Game, PlayersList
from game.utils.DataTypes import LootList
from game.utils.Dog import DogDirection
# from game.utils.GameSession import SessionState
from game.utils.ModelSerialization import serialize_dogs, serialize_loots
import logging
from game_exceptions.Exceptions import EmptyNameException, MapNotFoundException
from game.utils.FileUtils import read_json, write_json
import typing
from typing import Optional, Any

onlyPostMethodAllowedResp = {"code": "invalidMethod", "message": "Only POST method is expected"}
joinGameReqParseError = {"code": "invalidArgument", "message": "Join game request parse error"}
invalid_name_resp = {"code":  "invalidArgument", "message": "Invalid name"}
invaliMethodResp = {"code": "invalidMethod", "message": "Invalid method"}
auth_header_missing_resp = {"code": "invalidToken", "message": "Authorization header is missing"}
player_token_notfound_resp = {"code": "unknownToken", "message": "Player token has not been found"}
authHeaderRequiredResp = {"code": "invalidToken", "message": "Authorization header is required"}
invalidEndpointResp = {"code": "badRequest", "message": "Invalid endpoint"}
failedToParseTickResp = {"code": "invalidArgument", "message": "Failed to parse tick request JSON"}

invalid_map_resp = {"code": "mapNotFound", "message": "Map not found"}

logger = logging.getLogger(__name__)

MapList = list[{str, str}]
MapDict = {str, typing.Any}

async def handle_get_map_list(path: str) -> MapList:
	map_list = []
	try:
		read_task = asyncio.create_task(read_json(path))
		content = await read_task
		for item in content["maps"]:
			# dictn = dict()
			# dictn["id"] = item["id"]
			# dictn["name"] = item["name"]
			#
			# map_list.append(dictn)
			map_list.append({"id": item["id"], "name": item["name"]})
	except Exception as ex:
		print(ex.args)
	finally:
		return map_list

async def handle_get_map_info(path: str, map_name: str) -> Optional[dict]:
	map_dict = dict()
	try:
		read_task = asyncio.create_task(read_json(path))
		content = await read_task
		for item in content["maps"]:
			if item["id"] == map_name:
				map_dict = item
				break

	except:
		map_dict = None
	finally:
		return map_dict

def handle_auth_request(game: Game, model_: JoinModel) -> dict:
	try:
		token, player_id = game.add_player(model_.mapId, model_.userName)
		return {"authToken": token, "playerId": player_id}

	except EmptyNameException as ex:
		logger.exception("EmptyNameException during HandleAuthRequest")
		return invalid_name_resp

	except MapNotFoundException as ex:
		logger.exception("MapNotFoundException during HandleAuthRequest")
		return invalid_map_resp

	return invalid_map_resp


def handle_get_players_request(game: Game, auth_token: str) -> dict:
	if not auth_token:
		return auth_header_missing_resp

	if not game.has_session_with_auth_info(auth_token):
		return player_token_notfound_resp

	players = game.find_all_players_for_auth_info(auth_token)

	player_map = dict()
	for player in players:
		player_map[str(player.get_id())] = {"name": player.GetName()}

	return player_map

# bool IsValidAuthToken(const std::string& token, size_t valid_size)
# {
# 	 if(token.size() != valid_size)
# 		 return false;
#
# 	 for(auto i = 0; i < token.size(); ++i)
# 		 if((token[i] < '0') || (token[i] > '9') || (token[i] < 'a') || (token[i] > 'f'))
# 			 return false;
#
# 	 return true;
# }

def get_players_dog_info_response(players: PlayersList, loots: LootList) -> dict:
	return {"players": serialize_dogs(players), "lostObjects": serialize_loots(loots)}

def handle_get_game_state(game: Game, auth_token: str) -> dict:
	players = game.find_all_players_for_auth_info(auth_token)
	loots = game.get_loots_for_auth_info(auth_token)

	return get_players_dog_info_response(players, loots)


def handle_player_action(game: Game, auth_token: str, direction: DogDirection) -> dict:
	session = game.get_session_with_auth_info(auth_token)
	map_ = game.find_map(session.GetMap())
	map_speed = map_.dog_speed

	speed = map_speed if map_speed > 0.0 else game.get_default_dog_speed()
	player = game.GetPlayerWithAuthToken(auth_token)
	player.GetDog().set_speed(direction, speed)

	return {}

async def handle_get_game_records(game: Game, start: int, max_items:int) -> list[dict]:
	players = await game.get_retired_players(start, max_items)
	res = []
	for record in players:
		res.append({"name": record.name, "score": record.score, "playTime" : float(record.play_time) / 1000.0})

	return res

def handle_tick_action(game: Game, auth_token: str, delta: int) -> dict:
	# deltaTime = json_loader::ParseDeltaTimeRequest(body);
	# deltaTime = 100
	game.MoveDogs(delta)
	game.GenerateLoot(delta)

	return {}


# StringResponse ApiHandler::HandleTickAction(http::verb method, std::string_view auth_type,
# 											const std::string& body, unsigned http_version, bool keep_alive)
# {
# 	 StringResponse resp;
#
# 	 if(method != http::verb::post)
# 	 {
# 		 resp = MakeStringResponse(http::status::method_not_allowed,
# 	  	    			           json_serializer::MakeMappedResponce(invaliMethodResp),
#                                    http_version, keep_alive, ContentType::APPLICATION_JSON,
# 								   {{http::field::cache_control, "no-cache"sv}});
#
# 		 return resp;
# 	 }
# 	 if(ticker_)
# 	 {
# 		 resp = MakeStringResponse(http::status::bad_request,
# 	  		  					  json_serializer::MakeMappedResponce(invalidEndpointResp),
# 	  		   					  http_version, keep_alive, ContentType::APPLICATION_JSON,
# 								  {{http::field::cache_control, "no-cache"sv}});
# 	 }
# 	 else
# 	 {
# 		 try{
# 	  			int deltaTime = json_loader::ParseDeltaTimeRequest(body);
#
# 	  			game_.MoveDogs(deltaTime);
# 	  			game_.GenerateLoot(deltaTime);
# 	  			resp = MakeStringResponse(http::status::ok, "{}", http_version, keep_alive,
# 	  									  ContentType::APPLICATION_JSON, {{http::field::cache_control, "no-cache"sv}});
# 	  		}
# 	  		catch(BadDeltaTimeException& ex)
# 	  		{
# 	  			resp = MakeStringResponse(http::status::bad_request,
# 	  									  json_serializer::MakeMappedResponce(failedToParseTickResp),
# 	   									  http_version, keep_alive, ContentType::APPLICATION_JSON,
# 										  {{http::field::cache_control, "no-cache"sv}});
# 	  		}
# 	 }
#
# 	 return resp;
# }
#

