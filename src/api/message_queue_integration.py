"""
OMNI-AI Message Queue Integration
Integrates with external message queues (Redis, RabbitMQ) for distributed messaging
"""

import asyncio
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, Optional

from .communication_protocol import MessagePriority, MessageProtocol, MessageType

logger = logging.getLogger(__name__)


class QueueProvider(Enum):
    """Message queue provider enumeration."""

    REDIS = "redis"
    RABBITMQ = "rabbitmq"
    KAFKA = "kafka"
    AWS_SQS = "aws_sqs"


class MessageQueueIntegration:
    """
    Integration layer for external message queue systems.
    Supports Redis, RabbitMQ, and other message brokers.
    """

    def __init__(
        self,
        provider: QueueProvider = QueueProvider.REDIS,
        host: str = "localhost",
        port: int = 6379,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """
        Initialize message queue integration.

        Args:
            provider: Queue provider (Redis, RabbitMQ, etc.)
            host: Queue server host
            port: Queue server port
            username: Optional username for authentication
            password: Optional password for authentication
        """
        self.provider = provider
        self.host = host
        self.port = port
        self.username = username
        self.password = password

        self.protocol = MessageProtocol()
        self.connection = None
        self.is_connected = False

        # Message handlers
        self.message_handlers: Dict[MessageType, Callable] = {}

        logger.info(f"MessageQueueIntegration initialized with provider: {provider.value}")

    async def connect(self):
        """Connect to the message queue provider."""
        try:
            if self.provider == QueueProvider.REDIS:
                await self._connect_redis()
            elif self.provider == QueueProvider.RABBITMQ:
                await self._connect_rabbitmq()
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

            self.is_connected = True
            logger.info(f"Connected to {self.provider.value} message queue")

        except Exception as e:
            logger.error(f"Failed to connect to message queue: {str(e)}")
            raise

    async def _connect_redis(self):
        """Connect to Redis."""
        try:
            import redis.asyncio as aioredis

            # Create Redis connection
            if self.password:
                self.connection = await aioredis.from_url(
                    f"redis://:{self.password}@{self.host}:{self.port}",
                    encoding="utf-8",
                    decode_responses=True,
                )
            else:
                self.connection = await aioredis.from_url(
                    f"redis://{self.host}:{self.port}", encoding="utf-8", decode_responses=True
                )

            # Test connection
            await self.connection.ping()
            logger.info("Redis connection established")

        except ImportError:
            raise ImportError("Redis library not installed. Install with: pip install redis")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Redis: {str(e)}")

    async def _connect_rabbitmq(self):
        """Connect to RabbitMQ."""
        try:
            import aio_pika

            # Create connection URL
            if self.username and self.password:
                connection_url = f"amqp://{self.username}:{self.password}@{self.host}:{self.port}/"
            else:
                connection_url = f"amqp://{self.host}:{self.port}/"

            # Create connection
            self.connection = await aio_pika.connect_robust(connection_url)
            self.channel = await self.connection.channel()

            logger.info("RabbitMQ connection established")

        except ImportError:
            raise ImportError("aio_pika library not installed. Install with: pip install aio-pika")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to RabbitMQ: {str(e)}")

    async def disconnect(self):
        """Disconnect from the message queue provider."""
        if self.connection:
            if self.provider == QueueProvider.REDIS:
                await self.connection.close()
            elif self.provider == QueueProvider.RABBITMQ:
                await self.connection.close()

            self.is_connected = False
            logger.info(f"Disconnected from {self.provider.value} message queue")

    async def publish(
        self,
        topic: str,
        message: Dict[str, Any],
        priority: MessagePriority = MessagePriority.MEDIUM,
    ):
        """
        Publish a message to a topic/queue.

        Args:
            topic: Topic or queue name
            message: Message dictionary
            priority: Message priority
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to message queue")

        # Create protocol message
        protocol_message = self.protocol.create_message(
            message_type=MessageType(message.get("type", "agent_message")),
            data=message.get("data", {}),
            priority=priority,
        )

        try:
            if self.provider == QueueProvider.REDIS:
                await self._publish_redis(topic, protocol_message)
            elif self.provider == QueueProvider.RABBITMQ:
                await self._publish_rabbitmq(topic, protocol_message)

            logger.debug(f"Published message to topic: {topic}")

        except Exception as e:
            logger.error(f"Failed to publish message: {str(e)}")
            raise

    async def _publish_redis(self, topic: str, message: str):
        """Publish message to Redis."""
        await self.connection.publish(topic, message)

    async def _publish_rabbitmq(self, topic: str, message: str):
        """Publish message to RabbitMQ."""
        exchange = await self.channel.declare_exchange(
            topic, aio_pika.ExchangeType.FANOUT, durable=True  # noqa: F821
        )

        message_obj = aio_pika.Message(  # noqa: F821
            body=message.encode(), delivery_mode=aio_pika.DeliveryMode.PERSISTENT  # noqa: F821
        )

        await exchange.publish(message_obj, routing_key="")

    async def subscribe(self, topic: str, handler: Callable[[Dict[str, Any]], None]):
        """
        Subscribe to a topic/queue and register a message handler.

        Args:
            topic: Topic or queue name
            handler: Async callback function to handle messages
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to message queue")

        try:
            if self.provider == QueueProvider.REDIS:
                await self._subscribe_redis(topic, handler)
            elif self.provider == QueueProvider.RABBITMQ:
                await self._subscribe_rabbitmq(topic, handler)

            logger.info(f"Subscribed to topic: {topic}")

        except Exception as e:
            logger.error(f"Failed to subscribe to topic: {str(e)}")
            raise

    async def _subscribe_redis(self, topic: str, handler: Callable):
        """Subscribe to Redis channel."""
        pubsub = self.connection.pubsub()
        await pubsub.subscribe(topic)

        async def listen():
            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        parsed_message = self.protocol.parse_message(message["data"])
                        await handler(parsed_message)
                    except Exception as e:
                        logger.error(f"Error handling message: {str(e)}")

        asyncio.create_task(listen())

    async def _subscribe_rabbitmq(self, topic: str, handler: Callable):
        """Subscribe to RabbitMQ queue."""
        import aio_pika

        # Declare exchange and queue
        exchange = await self.channel.declare_exchange(
            topic, aio_pika.ExchangeType.FANOUT, durable=True
        )

        queue = await self.channel.declare_queue(
            f"{topic}_{datetime.utcnow().timestamp()}", durable=True
        )

        await queue.bind(exchange)

        async def process_message(message: aio_pika.IncomingMessage):
            async with message.process():
                try:
                    parsed_message = self.protocol.parse_message(message.body.decode())
                    await handler(parsed_message)
                except Exception as e:
                    logger.error(f"Error handling message: {str(e)}")

        await queue.consume(process_message)

    async def send_task(
        self,
        task_queue: str,
        task_id: str,
        description: str,
        parameters: Dict[str, Any],
        priority: str = "medium",
        agent_id: Optional[str] = None,
    ):
        """
        Send a task to a task queue.

        Args:
            task_queue: Task queue name
            task_id: Unique task identifier
            description: Task description
            parameters: Task parameters
            priority: Task priority
            agent_id: Optional specific agent ID
        """
        task_message = self.protocol.create_task_message(
            task_id=task_id,
            description=description,
            parameters=parameters,
            priority=priority,
            agent_id=agent_id,
        )

        await self.publish(task_queue, json.loads(task_message), MessagePriority.MEDIUM)

    async def broadcast_event(
        self, event_type: str, event_data: Dict[str, Any], source: Optional[str] = None
    ):
        """
        Broadcast an event to all subscribers.

        Args:
            event_type: Type of event
            event_data: Event data
            source: Optional event source
        """
        event_message = self.protocol.create_event(
            event_type=event_type, event_data=event_data, source=source
        )

        await self.publish("events", json.loads(event_message), MessagePriority.LOW)

    async def send_notification(
        self, notification_type: str, title: str, message: str, severity: str = "info"
    ):
        """
        Send a notification.

        Args:
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            severity: Notification severity
        """
        notification_message = self.protocol.create_notification(
            notification_type=notification_type, title=title, message=message, severity=severity
        )

        await self.publish(
            "notifications", json.loads(notification_message), MessagePriority.MEDIUM
        )

    async def register_handler(self, message_type: MessageType, handler: Callable):
        """
        Register a handler for a specific message type.

        Args:
            message_type: Type of message to handle
            handler: Handler function
        """
        self.message_handlers[message_type] = handler
        logger.debug(f"Registered handler for message type: {message_type.value}")

    async def handle_message(self, message: Dict[str, Any]):
        """
        Route a message to the appropriate handler.

        Args:
            message: Parsed message dictionary
        """
        message_type = message.get("message_type_enum")

        if message_type in self.message_handlers:
            handler = self.message_handlers[message_type]
            try:
                await handler(message)
            except Exception as e:
                logger.error(f"Error in message handler: {str(e)}")
        else:
            logger.warning(f"No handler registered for message type: {message_type.value}")

    async def get_queue_info(self) -> Dict[str, Any]:
        """
        Get information about queues.

        Returns:
            Queue information dictionary
        """
        info = {
            "provider": self.provider.value,
            "host": self.host,
            "port": self.port,
            "connected": self.is_connected,
        }

        if self.provider == QueueProvider.REDIS and self.is_connected:
            try:
                # Get Redis info
                info_queue_length = await self.connection.info("stats")
                info["queue_length"] = info_queue_length.get("total_commands_processed", 0)
            except Exception as e:
                logger.error(f"Error getting Redis info: {str(e)}")

        elif self.provider == QueueProvider.RABBITMQ and self.is_connected:
            try:
                # Get RabbitMQ queue info
                # Note: This would require additional setup
                info["queues"] = "Not implemented"
            except Exception as e:
                logger.error(f"Error getting RabbitMQ info: {str(e)}")

        return info
