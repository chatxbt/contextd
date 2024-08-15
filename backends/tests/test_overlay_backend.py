import unittest
from unittest.mock import AsyncMock
from backends.overlay_backend import OverlayStorageBackend
from backends.tests.test_base import TestBase
from backends.mongodb_backend import MongoDBBackend
from backends.redis_backend import RedisBackend
from backends.s3_backend import S3Backend

class TestMongoDBBackend(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mongodb_backend = MongoDBBackend(
            mongo_uri=cls.mongodb_container.get_connection_url(),
            db_name="test_db"
        )

    async def test_delete_context(self):
        context_key = "test_key"
        context_data = {"key": "value"}

        await self.mongodb_backend.save_context(context_key, context_data)
        await self.mongodb_backend.delete_context(context_key)
        deleted_context = await self.mongodb_backend.load_context(context_key)
        self.assertIsNone(deleted_context)

    async def test_list_contexts(self):
        context_keys = ["key1", "key2", "key3"]
        for key in context_keys:
            await self.mongodb_backend.save_context(key, {"data": key})

        listed_keys = await self.mongodb_backend.list_contexts()
        self.assertEqual(set(context_keys), set(listed_keys))

class TestRedisBackend(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.redis_backend = RedisBackend(
            redis_url=cls.redis_container.get_client(),
            enable_notifications=False
        )

    async def test_delete_context(self):
        context_key = "test_key"
        context_data = {"key": "value"}

        await self.redis_backend.save_context(context_key, context_data)
        await self.redis_backend.delete_context(context_key)
        deleted_context = await self.redis_backend.load_context(context_key)
        self.assertIsNone(deleted_context)

    async def test_list_contexts(self):
        context_keys = ["key1", "key2", "key3"]
        for key in context_keys:
            await self.redis_backend.save_context(key, {"data": key})

        listed_keys = await self.redis_backend.list_contexts()
        self.assertEqual(set(context_keys), set(listed_keys))

class TestS3Backend(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.minio_container_config = cls.minio_container.get_config()
        cls.s3_backend = S3Backend(
            bucket_name="test_bucket",
            aws_access_key_id=cls.minio_container_config["access_key"],
            aws_secret_access_key=cls.minio_container_config["secret_key"],
            region_name="us-east-1"
        )

    async def test_delete_context(self):
        context_key = "test_key"
        context_data = {"key": "value"}

        await self.s3_backend.save_context(context_key, context_data)
        await self.s3_backend.delete_context(context_key)
        deleted_context = await self.s3_backend.load_context(context_key)
        self.assertIsNone(deleted_context)

    async def test_list_contexts(self):
        context_keys = ["key1", "key2", "key3"]
        for key in context_keys:
            await self.s3_backend.save_context(key, {"data": key})

        listed_keys = await self.s3_backend.list_contexts()
        self.assertEqual(set(context_keys), set(listed_keys))

class TestOverlayStorageBackend(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.primary_backend = MongoDBBackend(
            mongo_uri=cls.mongodb_container.get_connection_url(),
            db_name="test_db"
        )
        cls.secondary_backend = RedisBackend(
            redis_url=cls.redis_container.get_client(),
            enable_notifications=False
        )
        cls.overlay_backend = OverlayStorageBackend(cls.primary_backend, cls.secondary_backend)

    async def test_save_and_load_context(self):
        context_key = "test_key"
        context_data = {"key": "value"}

        await self.overlay_backend.save_context(context_key, context_data)
        primary_context = await self.primary_backend.load_context(context_key)
        secondary_context = await self.secondary_backend.load_context(context_key)
        self.assertEqual(context_data, primary_context)
        self.assertEqual(context_data, secondary_context)

        loaded_context = await self.overlay_backend.load_context(context_key)
        self.assertEqual(context_data, loaded_context)

    async def test_publish_update(self):
        channel = "test_channel"
        await self.overlay_backend.publish_update(channel)
        # Assuming publish_update has side effects that can be checked

    async def test_subscribe_to_updates(self):
        channel = "test_channel"
        callback = AsyncMock()
        await self.overlay_backend.subscribe_to_updates(channel, callback)
        # Assuming subscribe_to_updates has side effects that can be checked

    async def test_acquire_and_release_lock(self):
        key = "test_key"
        lock_value = "test_value"
        lock_timeout = 1000

        lock_acquired = await self.overlay_backend.acquire_lock(key, lock_value, lock_timeout)
        self.assertTrue(lock_acquired)

        await self.overlay_backend.release_lock(key, lock_value)
        # Assuming release_lock has side effects that can be checked

if __name__ == "__main__":
    unittest.main()