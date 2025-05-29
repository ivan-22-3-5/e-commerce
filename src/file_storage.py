import os
from abc import ABC, abstractmethod

import aiofiles

from src.config import settings


class FileStorage(ABC):
    @abstractmethod
    async def save(self, file: bytes, path: str):
        pass

    @abstractmethod
    async def delete(self, path: str):
        pass


class LocalFileStorage(FileStorage):
    def __init__(self, base_path: str = 'files'):
        self.base_path = base_path.strip('/')

    async def save(self, file: bytes, path: str):
        filepath = self.base_path + "/" + path
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        async with aiofiles.open(filepath, 'wb') as f:
            await f.write(file)

    async def delete(self, path: str):
        filepath = self.base_path + "/" + path
        if os.path.exists(filepath):
            os.remove(filepath)


local_file_storage = LocalFileStorage(base_path=settings.FILES_DIR)
