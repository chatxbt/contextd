from backends.base import StorageBackend

class OverlayStorageBackend(StorageBackend):
    def __init__(self, primary_backend: StorageBackend, *secondary_backends: StorageBackend, enable_notifications=True):
        self.primary_backend = primary_backend
        self.secondary_backends = secondary_backends
        self.enable_notifications = enable_notifications

    async def load_context(self, context_key: str):
        return await self.primary_backend.load_context(context_key)

    async def save_context(self, context_key: str, context: dict):
        await self.primary_backend.save_context(context_key, context)
        for backend in self.secondary_backends:
            await backend.save_context(context_key, context)
        if self.enable_notifications:
            await self.primary_backend.publish_update(context_key)

    async def publish_update(self, channel: str):
        if self.enable_notifications:
            await self.primary_backend.publish_update(channel)

    async def subscribe_to_updates(self, channel: str, callback):
        if self.enable_notifications:
            await self.primary_backend.subscribe_to_updates(channel, callback)

    async def acquire_lock(self, key: str, lock_value: str, lock_timeout: int):
        return await self.primary_backend.acquire_lock(key, lock_value, lock_timeout)

    async def release_lock(self, key: str, lock_value: str):
        await self.primary_backend.release_lock(key, lock_value)
        for backend in self.secondary_backends:
            await backend.release_lock(key, lock_value)