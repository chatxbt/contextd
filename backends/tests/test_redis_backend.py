import unittest
import asyncio
from testcontainers.redis import RedisContainer
from backends.redis_backend import RedisBackend

class TestRedisBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.redis_container = RedisContainer()
        cls.redis_container.start()
        cls.backend = RedisBackend(
            redis_url=cls.redis_container.get_client(),
            enable_notifications=False  # Disable notifications for testing
        )

    @classmethod
    def tearDownClass(cls):
        cls.redis_container.stop()

    async def test_save_and_load_context(self):
        context_key = "test_key"
        context_data = {"key": "value"}
        await self.backend.save_context(context_key, context_data)
        loaded_context = await self.backend.load_context(context_key)
        self.assertEqual(context_data, loaded_context)

    async def test_acquire_and_release_lock(self):
        lock_key = "test_lock"
        lock_value = "test_value"
        lock_timeout = 10000  # 10 seconds

        # Acquire the lock
        lock_acquired = await self.backend.acquire_lock(lock_key, lock_value, lock_timeout)
        self.assertTrue(lock_acquired)

        # Release the lock
        lock_released = await self.backend.release_lock(lock_key, lock_value)
        self.assertEqual(lock_released, 1)

    async def test_publish_and_subscribe_updates(self):
        channel = "test_channel"
        update_received = asyncio.Event()

        async def callback():
            update_received.set()

        await self.backend.subscribe_to_updates(channel, callback)
        await self.backend.publish_update(channel)
        await asyncio.wait_for(update_received.wait(), timeout=5.0)

if __name__ == "__main__":
    unittest.main()