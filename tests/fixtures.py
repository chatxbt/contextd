import pytest
from backends.mongodb_backend import MongoDBBackend
from backends.redis_backend import RedisBackend
from backends.s3_backend import S3Backend
from testcontainers.mongodb import MongoDbContainer
from testcontainers.redis import RedisContainer
from testcontainers.minio import MinioContainer

@pytest.fixture(scope="module")
def mongodb_container():
    container = MongoDbContainer("mongo:latest")
    container.start()
    yield container
    container.stop()

@pytest.fixture(scope="module")
def redis_container():
    container = RedisContainer("redis:latest")
    container.start()
    yield container
    container.stop()

@pytest.fixture(scope="module")
def s3_container():
    container = MinioContainer("minio/minio:latest")
    container.start()
    yield container
    container.stop()

@pytest.fixture
def mongodb_backend(mongodb_container):
    return MongoDBBackend(
        mongo_uri=mongodb_container.get_connection_url(),
        db_name="test_db"
    )

@pytest.fixture
def redis_backend(redis_container):
    return RedisBackend(
        redis_url=redis_container.get_connection_url()
    )

@pytest.fixture
def s3_backend(s3_container):
    return S3Backend(
        bucket_name="test_bucket",
        aws_access_key_id="test_access_key",
        aws_secret_access_key="test_secret_key",
        region_name="us-east-1"
    )