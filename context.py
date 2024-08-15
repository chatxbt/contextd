import uuid
import asyncio
from backends.base import StorageBackend
from common.logger import configure_logging
from common.event import event_emitter 

# Configure the logger
logger = configure_logging()

class Contextd:
    def __init__(self, context_key: str, storage_backend: StorageBackend, enable_notifications=True):
        self.context_key = context_key
        self.context = {}
        self.storage = storage_backend
        self.lock_key = f"{self.context_key}_lock"
        self.lock_value = str(uuid.uuid4())  # Unique identifier for the lock owner
        self.enable_notifications = enable_notifications
        logger.debug(f"Initialized Contextd with context_key: {self.context_key}")

    async def initialize(self):
        logger.debug("Initializing context")
        self.context = await self.storage.load_context(self.context_key)
        if self.enable_notifications:
            await self.storage.subscribe_to_updates(self.context_key, self.load_context)
        logger.debug("Context initialized and subscription to updates set")

    async def load_context(self):
        logger.debug("Loading context")
        self.context = await self.storage.load_context(self.context_key)
        logger.debug(f"Context loaded: {self.context}")

    async def save_context(self):
        logger.debug(f"Saving context: {self.context}")
        await self.storage.save_context(self.context_key, self.context)
        event_emitter.emit('context_updated', self.context)  # Emit the event using the global event emitter
        logger.debug("Context saved")

    async def acquire_lock(self, lock_timeout=10000, retry_delay=0.1, max_retries=50):
        logger.debug(f"Acquiring lock with key: {self.lock_key}")
        for _ in range(max_retries):
            lock_acquired = await self.storage.acquire_lock(self.lock_key, self.lock_value, lock_timeout)
            if lock_acquired:
                logger.debug("Lock acquired")
                return True
            await asyncio.sleep(retry_delay)
        logger.debug("Failed to acquire lock")
        return False

    async def release_lock(self):
        logger.debug(f"Releasing lock with key: {self.lock_key}")
        await self.storage.release_lock(self.lock_key, self.lock_value)
        logger.debug("Lock released")

    async def update_context(self, key: str, value):
        logger.debug(f"Updating context key: {key} with value: {value}")
        if await self.acquire_lock():
            try:
                self.context[key] = value
                await self.save_context()
            finally:
                await self.release_lock()
        else:
            logger.error("Failed to acquire lock for updating context")
            raise Exception("Failed to acquire lock for updating context")

    async def transactional_update(self, operations):
        logger.debug(f"Performing transactional update with operations: {operations}")
        if await self.acquire_lock():
            try:
                for key, value in operations.items():
                    self.context[key] = value
                await self.save_context()
            finally:
                await self.release_lock()
        else:
            logger.error("Failed to acquire lock for transactional update")
            raise Exception("Failed to acquire lock for transactional update")

    def get_context(self):
        logger.debug(f"Getting context: {self.context}")
        return self.context