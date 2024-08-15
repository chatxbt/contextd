# Contextd

A Distributed Context Management System with Redis

## Overview

Contextd is an asynchronous, distributed context management system designed to work across multiple servers. It leverages Redis for storing the context and provides mechanisms to synchronize context updates across different instances using Redis Pub/Sub. The class also incorporates distributed locking to ensure safe, concurrent updates to individual context keys, making it ideal for use in distributed systems where multiple processes or servers need to share and update a common state.

## Features

	•	Asynchronous Operations: All operations are non-blocking and designed for use in an asynchronous environment.
	•	Distributed Context Management: Context is stored in Redis, allowing it to be shared across multiple instances or servers.
	•	Event-Based Context Synchronization: Automatically synchronizes context updates across all instances using Redis Pub/Sub.
	•	Key-Based Distributed Locking: Ensures that updates to individual context keys are thread-safe and free from race conditions.
	•	Retry Mechanism: Built-in retries for acquiring locks ensure robustness in high-contention environments.

## Installation

To use contextd, you need to install the following Python package:

```bash
pip install aioredis
```

## Initialization

### Creating an Instance

To create an instance of Contextd, you need to specify a context key that uniquely identifies the context object in Redis. Optionally, you can also specify Redis connection details and the Pub/Sub channel name.

```python
from contextd import Contextd

context = Contextd(
    context_key="my_cxtd",
    redis_host='localhost',
    redis_port=6379,
    redis_db=0,
    pubsub_channel='context_updates'
)
```

### Initialize the Context

Before using the context, you must initialize it, which establishes the Redis connection, loads the initial context, and starts listening for updates.

```python
await context.initialize()
```

## Usage

### Updating the Context

You can update individual keys in the context using the update_context method. This method automatically handles acquiring and releasing a distributed lock for the specific key.

```python
await context.update_context("user", {"name": "John Doe", "email": "john@example.com"})
```

### Transactional Updates

For updating multiple keys in a single atomic operation, use the transactional_update method. This ensures that all updates are applied together under the protection of a lock.

```python
await context.transactional_update({
    "user": {"name": "Jane Doe", "email": "jane@example.com"},
    "logged_in": True
})
```

### Retrieving the Context

To retrieve the current context, use the get_context method:

```python
current_context = context.get_context()
print(current_context)
```

### Listening for Updates

Contextd automatically listens for updates from other instances. When an update is received, the context is refreshed to reflect the latest state. This happens automatically, so you don’t need to manage it manually.

## Example

Here’s a full example demonstrating how to use Contextd:

```python
import asyncio
from contextd import Contextd

async def main():
    # Create and initialize the context
    cxtd = Contextd(context_key="my_cxtd")
    await cxtd.initialize()

    # Update context
    await cxtd.update_context("user", {"name": "John Doe", "email": "john@example.com"})

    # Perform transactional updates
    await cxtd.transactional_update({
        "user": {"name": "Jane Doe", "email": "jane@example.com"},
        "logged_in": True
    })

    # Retrieve current context
    current_context = cxtd.get_context()
    print(f"Current Context: {current_context}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Configuration

### Redis Connection

By default, the class connects to Redis using localhost on port 6379 with database 0. You can customize these settings through the constructor:

```python
cxtd = Contextd(
    context_key="my_cxtd",
    redis_host='my-redis-server',
    redis_port=6380,
    redis_db=1
)
```

### Locking and Retry Mechanism

The acquire_lock method allows for setting a custom lock timeout, retry delay, and maximum number of retries:

```python
lock_acquired = await context.acquire_lock(
    key="user", 
    lock_timeout=15000,  # 15 seconds
    retry_delay=0.2,     # 200 ms
    max_retries=100      # Retry up to 100 times
)
```

## Best Practices

	•	Use Key-Based Locking: Each context key is locked independently, allowing different keys to be updated concurrently without conflicts.
	•	Optimize Retry Settings: Tune the retry delay and maximum retries based on your application’s concurrency requirements and Redis latency.
	•	Monitor Redis: Since Redis is central to this system, monitor its performance and availability, especially in production environments.

## Troubleshooting

	•	Lock Contention: If you experience high contention on locks, consider reviewing your application’s design to reduce simultaneous updates to the same keys or increase the retry count and delay.
	•	Redis Connection Issues: Ensure that the Redis server is reachable from all instances that use Contextd. If you experience connection timeouts or errors, verify the Redis configuration and network settings.

## TODO

1. Add support for local caching
2. Add support for multiple storage backends (Redis, SQLite, S3, etc.)

## License

Contextd is licensed under the MIT License. See the LICENSE file for more details.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss your ideas or report bugs.

## Contact

For questions or support, please open an issue on the GitHub repository.

This documentation should provide a comprehensive guide for using Contextd in your distributed applications.
