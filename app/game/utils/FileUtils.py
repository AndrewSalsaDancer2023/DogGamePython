import aiofiles
from typing import Any
from pathlib import Path
import json

async def read_json(path: str) -> Any:
    fullpath = str(Path.cwd()) + path
    async with aiofiles.open(fullpath, mode='r') as file:
        content = await file.read()
        data = json.loads(content)
        return data

async def write_json(path: str, content: list):
    fullpath = str(Path.cwd()) + path
    async with aiofiles.open(fullpath, mode='w') as file:
        file_content = json.dumps(content)
        # print('**********file content**************')
        # print(file_content)
        await file.write(file_content)
        await file.flush()
