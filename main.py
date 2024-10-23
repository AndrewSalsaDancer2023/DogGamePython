from fastapi import FastAPI
from contextlib import asynccontextmanager

# from functools import lru_cache
from game_exceptions.Exceptions import MapNotFoundException
from fastapi import Request
from models.ReqModel import JoinModel, MoveModel, TickModel, RecordModel
from responses import JsonResponse
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing_extensions import Annotated
import logging
from game.utils.logger import configure_logging
from game.Game import create_game
from request_handlers.Handlers import (handle_auth_request, handle_get_players_request, handle_tick_action,
                                       handle_get_game_state, handle_player_action, handle_get_game_records,
                                       handle_get_map_list, handle_get_map_info)

import asyncio
from game.utils.FileUtils import read_json
from typing import Optional
from game.Game import Game
from game.utils.GameTimer import GameTimer
from models.ConcreteRepository import ConcreteRepository, create_database
# from game.utils.ModelSerialization import restore_sessions
# from game.utils.FileUtils import write_json
# from request_handlers.Middleware import PyInstrumentMiddleWare

config_path: str = "/data/config.json"
configure_logging(level=logging.INFO, log_name='bugs_log')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        read_task = asyncio.create_task(read_json(config_path))
        config_content = await read_task
        global dog_game, game_timer

        # await create_database('postgres', 'records')
        # await repository.create_table()
        dog_game = create_game(config_content, repository, game_exception_handler)
        game_timer = GameTimer(dog_game.get_tick_period())
        game_timer.start(dog_game.timer_handler)
        yield
        # await repository.dispose_repository()
        logger.info('Application shutdown')
    except Exception as ex:
        print(ex.args)

async def game_exception_handler() -> None:
    try:
        read_task = asyncio.create_task(read_json('/sessions_state.tmp'))
        session_content = await read_task
        dog_game.restore_sessions(session_content)
    except Exception as ex:
        print(ex.args) #shutdown

app = FastAPI(lifespan=lifespan)
security = HTTPBearer()
repository = ConcreteRepository()
dog_game = Optional[Game]
game_timer = None

# app.add_middleware(PyInstrumentMiddleWare)

# @app.on_event('startup')
# async def create_dog_game() -> None:
#     read_task = asyncio.create_task(read_json(config_path))
#     config_content = await read_task
#     global dog_game, game_timer
#     dog_game = create_game(config_content)
#     game_timer = GameTimer(dog_game.get_tick_period())
#     game_timer.start(dog_game.timer_handler)


#################################################
# from fastapi.security import OAuth2PasswordBearer
# from typing_extensions import Annotated
#
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# @lru_cache
# def read_maps():
#


@app.exception_handler(MapNotFoundException)
async def map_not_found_handler(request: Request, exc: MapNotFoundException):
    return exc.getResponse()
    # return JSONResponse(status_code = 404, content = { "code" : "mapNotFound", "message": "Map not found"})


@app.get("/api/v1/maps")
async def read_maps():
    return await handle_get_map_list(config_path)
    # return config_reader.getMapsInfo()


@app.get("/api/v1/maps/{map_id}")
async def read_item(map_id: str):
    resp = await handle_get_map_info(config_path, map_id)

    if not resp:
        raise MapNotFoundException(name="Map not found")

    return JsonResponse.create_success_response(resp)


@app.post("/api/v1/game/join")
async def join_game(model: JoinModel):
    # resp = await handle_get_game_records(dog_game, 0, 100)
    resp = handle_auth_request(dog_game, model)
    if resp.get('code') is not None:
        return JsonResponse.create_failed_response(resp)

    return JsonResponse.create_success_response(resp)


@app.get("/api/v1/game/players")
def get_players_info(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]):
    resp = handle_get_players_request(dog_game, credentials.credentials)
    # logger.info("inside /game/players", str(resp))
    if resp.get('code') is not None:
        return JsonResponse.create_failed_response(resp, 401)

    return JsonResponse.create_success_response(resp)


@app.get("/api/v1/game/state")
def get_players_info(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]):
    resp = handle_get_game_state(dog_game, credentials.credentials)
    logger.info(str(resp))
    if resp.get('code') is not None:
        return JsonResponse.create_failed_response(resp, 401)

    return JsonResponse.create_success_response(resp)


@app.post("/api/v1/game/player/action")
def join_player(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)], model: MoveModel):
    resp = handle_player_action(dog_game, credentials.credentials, model.move)
    if resp.get('code') is not None:
        return JsonResponse.create_failed_response(resp, 401)

    return JsonResponse.create_success_response(resp)


@app.post("/api/v1/game/tick")
def join_player(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)], model: TickModel):
    resp = handle_tick_action(dog_game, credentials.credentials, model.timeDelta)
    if resp.get('code') is not None:
        return JsonResponse.create_failed_response(resp, 401)

    return JsonResponse.create_success_response(resp)

@app.get("/api/v1/game/records")
async def get_players_info():
    try:
        resp = await handle_get_game_records(dog_game, 0, 100)
        # logger.info(str(resp))

        return JsonResponse.create_success_records_response(resp)
    except Exception as ex:
        print(ex.args)

if __name__ == "__main__":
    import uvicorn

    # uvicorn.run(app, host="0.0.0.0", port=8080)
    uvicorn.run(app, host="localhost", port=8080)
