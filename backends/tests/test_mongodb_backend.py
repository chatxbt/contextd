import unittest
from backends.mongodb_backend import MongoDBBackend
from backends.tests.test_base import TestBase


class TestMongoDBBackend(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend = MongoDBBackend(
            mongo_uri=cls.mongodb_container.get_connection_url(),
            db_name="test_db"
        )

    async def test_save_and_load_context(self):
        context_key = "test_key"
        context_data = {"key": "value"}
        await self.backend.save_context(context_key, context_data)
        loaded_context = await self.backend.load_context(context_key)
        self.assertEqual(context_data, loaded_context)

if __name__ == "__main__":
    unittest.main()