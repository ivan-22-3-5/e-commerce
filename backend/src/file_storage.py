import os
from abc import ABC, abstractmethod

from src.config import settings


class FileStorage(ABC):
    @abstractmethod
    async def save(self, file: str, path: str):
        pass


class LocalFileStorage(FileStorage):
    def __init__(self, base_path: str = 'files'):
        self.base_path = base_path.strip('/')

    async def save(self, file: bytes, path: str):
        filepath = self.base_path + "/" + path
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'wb') as f:
            f.write(file)


local_file_storage = LocalFileStorage(base_path=settings.FILES_DIR)
