from abc import ABC, abstractmethod

class StorageBackend(ABC):
    @abstractmethod
    async def load_context(self, context_key: str):
        pass

    @abstractmethod
    async def save_context(self, context_key: str, context: dict):
        pass

    @abstractmethod
    async def publish_update(self, channel: str):
        pass

    @abstractmethod
    async def subscribe_to_updates(self, channel: str, callback):
        pass

    @abstractmethod
    async def acquire_lock(self, key: str, lock_value: str, lock_timeout: int):
        pass

    @abstractmethod
    async def release_lock(self, key: str, lock_value: str):
        pass