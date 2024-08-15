import unittest
from testcontainers.mongodb import MongoDbContainer
from testcontainers.redis import RedisContainer
from testcontainers.minio import MinioContainer

class TestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mongodb_container = MongoDbContainer("mongo:latest")
        cls.mongodb_container.start()
        
        cls.redis_container = RedisContainer("redis:latest")
        cls.redis_container.start()
        
        cls.minio_container = (
            MinioContainer("minio/minio:latest").with_env("MINIO_ACCESS_KEY", "minioadmin").with_env("MINIO_SECRET_KEY", "minioadmin")
        )
        cls.minio_container.start()

    @classmethod
    def tearDownClass(cls):
        cls.mongodb_container.stop()
        cls.redis_container.stop()
        cls.minio_container.stop()