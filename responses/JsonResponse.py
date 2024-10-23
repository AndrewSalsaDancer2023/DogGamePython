from fastapi.responses import JSONResponse
from typing import Optional
import json


def map_string_len(convert_map: dict) -> int:
    return len(json.dumps(convert_map))

def create_success_response(content: dict):
    return JSONResponse(status_code=200, content=content)

def create_success_records_response(content: list[dict]):
    return JSONResponse(status_code=200, content=content)

def create_failed_response(content: dict, code: int = 404):
    return JSONResponse(status_code=code, content=content)

def create_join_response_succeed(content: dict):
    try:
        # player_headers = {"Cache-Control": "no-cache", "Content-Type": "application/json",
        #                   "Content-Length": map_string_len(content)}
        player_headers = {}
        player_headers["Cache-Control"] = "no-cache"
        player_headers["Content-Type"] = "application/json"
        player_headers["Content-Length"] = map_string_len(content)

        return JSONResponse(status_code=200, content=content)#, headers=player_headers)
    except Exception as ex:
        print(ex)

def create_join_response_failed(content: dict):
    player_headers = {"Cache-Control": "no-cache", "Content-Type": "application/json",
                      "Content-Length": map_string_len(content)}

    return JSONResponse(status_code=404, content=content)# headers=player_headers)


def create_get_players_info_response(content: Optional[dict]):
    player_headers = {}
    player_headers["Cache-Control"] = "no-cache"
    player_headers["Content-Type"] = "application/json"
    new_content = content if content is not None else {}
    player_headers["Content-Length"] = map_string_len(new_content)

    return JSONResponse(status_code=200, content=new_content)# headers=player_headers)


def create_get_players_state_response(content: Optional[dict]):
    player_headers = {}
    player_headers["Cache-Control"] = "no-cache"
    player_headers["Content-Type"] = "application/json"
    new_content = content if content is not None else {}
    player_headers["Content-Length"] = map_string_len(new_content)

    return JSONResponse(status_code=200, content=new_content)# headers=player_headers)


def create_move_response_succeed(content: dict):
    # player_headers = {"Cache-Control": "no-cache", "Content-Type": "application/json",
    #                   "Content-Length": map_string_len(content)}

    return JSONResponse(status_code=200, content=content)# headers=player_headers)


def create_move_response_failed(content: dict):
    player_headers = {"Cache-Control": "no-cache", "Content-Type": "application/json",
                      "Content-Length": map_string_len(content)}

    return JSONResponse(status_code=401, content=content)# headers=player_headers)
