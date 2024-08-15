import unittest
import asyncio
from contextlib import ExitStack
from unittest.mock import Mock
from testcontainers.mongodb import MongoDbContainer
from backends.mongodb_backend import MongoDBBackend
from context import Contextd

class TestContextd(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.mongodb_container = self.stack.enter_context(MongoDbContainer())
        self.mongo_uri = self.mongodb_container.get_connection_url()
        self.storage_backend = Mock(spec=MongoDBBackend)
        self.context_key = "test_context"
        self.contextd = Contextd(self.context_key, self.storage_backend)

    def tearDown(self):
        self.stack.close()

    def test_initialize(self):
        async def run_test():
            await self.contextd.initialize()
            self.storage_backend.load_context.assert_awaited_with(self.context_key)
            self.storage_backend.subscribe_to_updates.assert_awaited_with(self.context_key, self.contextd.load_context)

        asyncio.run(run_test())

    def test_load_context(self):
        async def run_test():
            context_data = {"key": "value"}
            self.storage_backend.load_context.return_value = context_data
            await self.contextd.load_context()
            self.assertEqual(self.contextd.context, context_data)
            self.storage_backend.load_context.assert_awaited_with(self.context_key)

        asyncio.run(run_test())

    def test_save_context(self):
        async def run_test():
            self.contextd.context = {"key": "value"}
            await self.contextd.save_context()
            self.storage_backend.save_context.assert_awaited_with(self.context_key, self.contextd.context)

        asyncio.run(run_test())

    def test_acquire_lock(self):
        async def run_test():
            self.storage_backend.acquire_lock.return_value = True
            lock_acquired = await self.contextd.acquire_lock()
            self.assertTrue(lock_acquired)
            self.storage_backend.acquire_lock.assert_awaited_with(self.contextd.lock_key, self.contextd.lock_value, 10000)

        asyncio.run(run_test())

    def test_release_lock(self):
        async def run_test():
            await self.contextd.release_lock()
            self.storage_backend.release_lock.assert_awaited_with(self.contextd.lock_key, self.contextd.lock_value)

        asyncio.run(run_test())

    def test_update_context(self):
        async def run_test():
            self.storage_backend.acquire_lock.return_value = True
            await self.contextd.update_context("key", "value")
            self.assertEqual(self.contextd.context["key"], "value")
            self.storage_backend.save_context.assert_awaited_with(self.context_key, self.contextd.context)
            self.storage_backend.release_lock.assert_awaited_with(self.contextd.lock_key, self.contextd.lock_value)

        asyncio.run(run_test())

    def test_transactional_update(self):
        async def run_test():
            self.storage_backend.acquire_lock.return_value = True
            operations = {"key1": "value1", "key2": "value2"}
            await self.contextd.transactional_update(operations)
            self.assertEqual(self.contextd.context["key1"], "value1")
            self.assertEqual(self.contextd.context["key2"], "value2")
            self.storage_backend.save_context.assert_awaited_with(self.context_key, self.contextd.context)
            self.storage_backend.release_lock.assert_awaited_with(self.contextd.lock_key, self.contextd.lock_value)

        asyncio.run(run_test())

    def test_get_context(self):
        self.contextd.context = {"key": "value"}
        self.assertEqual(self.contextd.get_context(), {"key": "value"})

if __name__ == "__main__":
    unittest.main()