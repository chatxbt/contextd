import asyncio_redis
import json

from backends.base import StorageBackend
from backends.notifications import RedisNotification

class RedisBackend(StorageBackend):
    def __init__(self, redis_url, enable_notifications=True):
        self.redis = asyncio_redis.Connection.create(host=redis_url)
        self.enable_notifications = enable_notifications
        self.notification = RedisNotification(redis_url)

    async def load_context(self, context_key: str):
        context_data = await self.redis.get(context_key)
        return json.loads(context_data) if context_data else {}

    async def save_context(self, context_key: str, context: dict):
        await self.redis.set(context_key, json.dumps(context))
        if self.enable_notifications:
            await self.notification.publish_update(context_key)

    async def publish_update(self, channel: str):
        if self.enable_notifications:
            await self.notification.publish_update(channel)

    async def subscribe_to_updates(self, channel: str, callback):
        if self.enable_notifications:
            await self.notification.subscribe_to_updates(channel, callback)

    async def acquire_lock(self, key: str, lock_value: str, lock_timeout: int):
        return await self.redis.set(key, lock_value, nx=True, px=lock_timeout)

    async def release_lock(self, key: str, lock_value: str):
        script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        return await self.redis.eval(script, keys=[key], args=[lock_value])