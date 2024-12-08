from fastapi.responses import JSONResponse

class MapNotFoundException(Exception):
    def __init__(self, name: str):
        self.name = name

    def getResponse(self):
        return JSONResponse(status_code=404, content={"code": "mapNotFound", "message": "Map not found"})

class UnknownRoadOrientation(Exception):
    def __init__(self, name:str):
        self.name = name

class MapNotFoundException(Exception): # "Map not found"
    def __init__(self, name:str):
        self.name = name


class EmptyNameException(Exception): # "Empty player name specified"
    def __init__(self, name:str):
        self.name = name

class ParsingJsonException(Exception): # "Invalid Json"
    def __init__(self, name:str):
        self.name = name


class MetodNotAllowedException(Exception): # "Invalid HTTP method"
    def __init__(self, name: str):
        self.name = name

class PlayerAbsentException(Exception): # "No player with specified token"
    def __init__(self, name: str):
        self.name = name

class DogSpeedException(Exception): # "Impossible to set dog speed"
    def __init__(self, name: str):
        self.name = name

class InvalidSessionException(Exception): # "Impossible to find session with specified auth info"
    def __init__(self, name: str):
        self.name = name

class BadDeltaTimeException(Exception): # "Wrong value for timeDelta parameter"
    def __init__(self, name: str):
        self.name = name

class LootNotSpecifiedException(Exception): # "Wrong value for timeDelta parameter"
    def __init__(self, name: str):
        self.name = name

class RoadNotSpecifiedException(Exception): # "Wrong value for timeDelta parameter"
    def __init__(self, name: str):
        self.name = name