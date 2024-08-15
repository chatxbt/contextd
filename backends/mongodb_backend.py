import motor.motor_asyncio
import json
from datetime import datetime, timedelta

from backends.base import StorageBackend
from backends.notifications import MongoNotification

class MongoDBBackend(StorageBackend):
    def __init__(self, mongo_uri, db_name, enable_notifications=True):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
        self.db = self.client[db_name]
        self.enable_notifications = enable_notifications
        self.notification = MongoNotification(mongo_uri, db_name)

    async def load_context(self, context_key: str):
        document = await self.db.contexts.find_one({"context_key": context_key})
        return document.get('context', {}) if document else {}

    async def save_context(self, context_key: str, context: dict):
        await self.db.contexts.update_one(
            {"context_key": context_key},
            {"$set": {"context": context}},
            upsert=True
        )
        if self.enable_notifications:
            await self.notification.publish_update(context_key)

    async def publish_update(self, channel: str):
        if self.enable_notifications:
            await self.notification.publish_update(channel)

    async def subscribe_to_updates(self, channel: str, callback):
        if self.enable_notifications:
            await self.notification.subscribe_to_updates(channel, callback)

    async def acquire_lock(self, key: str, lock_value: str, lock_timeout: int):
        expire_at = datetime.utcnow() + timedelta(milliseconds=lock_timeout)
        result = await self.db.locks.update_one(
            {"_id": key, "lock_value": {"$exists": False}},
            {"$set": {"lock_value": lock_value, "expire_at": expire_at}},
            upsert=True
        )
        return result.modified_count == 1

    async def release_lock(self, key: str, lock_value: str):
        await self.db.locks.delete_one({"_id": key, "lock_value": lock_value})