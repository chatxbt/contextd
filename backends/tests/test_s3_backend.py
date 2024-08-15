import unittest
import asyncio
from testcontainers.minio import MinioContainer
from backends.s3_backend import S3Backend

class TestS3Backend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.minio_container = (
            MinioContainer("minio/minio:latest").with_env("MINIO_ACCESS_KEY", "minioadmin").with_env("MINIO_SECRET_KEY", "minioadmin")
        )
        cls.minio_container.start()
        cls.minio_container_config = cls.minio_container.get_config()
        cls.backend = S3Backend(
            bucket_name="test_bucket",
            aws_access_key_id=cls.minio_container_config["access_key"],
            aws_secret_access_key=cls.minio_container_config["secret_key"],
            region_name="us-east-1"
        )

    @classmethod
    def tearDownClass(cls):
        cls.minio_container.stop()

    async def test_save_and_load_context(self):
        context_key = "test_key"
        context_data = {"key": "value"}
        await self.backend.save_context(context_key, context_data)
        loaded_context = await self.backend.load_context(context_key)
        self.assertEqual(context_data, loaded_context)

    async def test_publish_update(self):
        channel = "test_channel"
        await self.backend.publish_update(channel)
        # No assertions needed as publish_update doesn't return anything

    async def test_subscribe_to_updates(self):
        channel = "test_channel"
        update_received = asyncio.Event()

        async def callback():
            update_received.set()

        await self.backend.subscribe_to_updates(channel, callback)
        await self.backend.publish_update(channel)
        await asyncio.wait_for(update_received.wait(), timeout=5.0)

    async def test_acquire_and_release_lock(self):
        key = "test_key"
        lock_value = "test_value"
        lock_timeout = 10000  # 10 seconds

        lock_acquired = await self.backend.acquire_lock(key, lock_value, lock_timeout)
        self.assertTrue(lock_acquired)

        lock_released = await self.backend.release_lock(key, lock_value)
        self.assertTrue(lock_released)

if __name__ == "__main__":
    unittest.main()