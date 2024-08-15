import boto3
import json
from datetime import datetime, timedelta

from backends.base import StorageBackend
from backends.notifications import RedisNotification, MongoNotification

class S3Backend(StorageBackend):
    def __init__(self, bucket_name, aws_access_key_id, aws_secret_access_key, region_name, notification_type='redis', redis_url=None, mongo_uri=None, db_name=None, enable_notifications=True):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        self.bucket_name = bucket_name
        self.enable_notifications = enable_notifications
        
        if notification_type == 'mongo' and mongo_uri and db_name:
            self.notification = MongoNotification(mongo_uri, db_name)
        elif notification_type == 'redis' and redis_url:
            self.notification = RedisNotification(redis_url)
        else:
            self.notification = None

    async def load_context(self, context_key: str):
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=context_key)
            return json.loads(response['Body'].read().decode('utf-8'))
        except self.s3.exceptions.NoSuchKey:
            return {}

    async def save_context(self, context_key: str, context: dict):
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=context_key,
            Body=json.dumps(context).encode('utf-8')
        )
        if self.enable_notifications and self.notification:
            await self.notification.publish_update(context_key)

    async def publish_update(self, channel: str):
        if self.enable_notifications and self.notification:
            await self.notification.publish_update(channel)

    async def subscribe_to_updates(self, channel: str, callback):
        if self.enable_notifications and self.notification:
            await self.notification.subscribe_to_updates(channel, callback)

    async def acquire_lock(self, key: str, lock_value: str, lock_timeout: int):
        try:
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=lock_value,
                Metadata={'expire_at': (datetime.utcnow() + timedelta(milliseconds=lock_timeout)).isoformat()},
                ConditionExpression='attribute_not_exists(lock_value)'
            )
            return True
        except self.s3.exceptions.ConditionalCheckFailedException:
            return False

    async def release_lock(self, key: str, lock_value: str):
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            if response['Body'].read().decode('utf-8') == lock_value:
                self.s3.delete_object(Bucket=self.bucket_name, Key=key)
        except self.s3.exceptions.NoSuchKey:
            pass