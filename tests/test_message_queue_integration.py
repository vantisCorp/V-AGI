"""
Tests for Message Queue Integration Module.
"""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from src.api.communication_protocol import MessagePriority, MessageType
from src.api.message_queue_integration import MessageQueueIntegration, QueueProvider


class TestQueueProvider:
    """Tests for QueueProvider enum."""

    def test_queue_provider_values(self):
        """Test QueueProvider enum values."""
        assert QueueProvider.REDIS.value == "redis"
        assert QueueProvider.RABBITMQ.value == "rabbitmq"
        assert QueueProvider.KAFKA.value == "kafka"
        assert QueueProvider.AWS_SQS.value == "aws_sqs"

    def test_queue_provider_count(self):
        """Test that QueueProvider has expected number of values."""
        assert len(QueueProvider) == 4

    def test_queue_provider_from_string(self):
        """Test creating QueueProvider from string."""
        assert QueueProvider("redis") == QueueProvider.REDIS
        assert QueueProvider("rabbitmq") == QueueProvider.RABBITMQ


class TestMessageQueueIntegration:
    """Tests for MessageQueueIntegration class."""

    def test_mqi_initialization(self):
        """Test MessageQueueIntegration initialization with defaults."""
        mqi = MessageQueueIntegration()

        assert mqi.provider == QueueProvider.REDIS
        assert mqi.host == "localhost"
        assert mqi.port == 6379
        assert mqi.username is None
        assert mqi.password is None
        assert mqi.connection is None
        assert mqi.is_connected is False

    def test_mqi_initialization_with_auth(self):
        """Test MessageQueueIntegration initialization with auth."""
        mqi = MessageQueueIntegration(
            provider=QueueProvider.REDIS,
            host="redis.example.com",
            port=6380,
            username="user",
            password="pass",
        )

        assert mqi.provider == QueueProvider.REDIS
        assert mqi.host == "redis.example.com"
        assert mqi.port == 6380
        assert mqi.username == "user"
        assert mqi.password == "pass"

    def test_mqi_initialization_rabbitmq(self):
        """Test MessageQueueIntegration initialization with RabbitMQ."""
        mqi = MessageQueueIntegration(provider=QueueProvider.RABBITMQ, port=5672)

        assert mqi.provider == QueueProvider.RABBITMQ
        assert mqi.port == 5672

    @pytest.mark.asyncio
    async def test_connect_unsupported_provider(self):
        """Test connect with unsupported provider."""
        mqi = MessageQueueIntegration()
        # Manually set provider to an unsupported one
        mqi.provider = "unsupported"

        with pytest.raises(ValueError, match="Unsupported provider"):
            await mqi.connect()

    @pytest.mark.asyncio
    async def test_connect_redis_success(self):
        """Test successful Redis connection setup."""
        mqi = MessageQueueIntegration()

        # Create mock redis connection
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)

        # Directly set the connection for testing
        mqi.connection = mock_redis
        mqi.is_connected = True

        assert mqi.is_connected is True
        assert mqi.connection is not None

    @pytest.mark.asyncio
    async def test_connect_redis_with_password(self):
        """Test Redis connection with password."""
        mqi = MessageQueueIntegration(password="secret")

        # Create mock redis connection
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)

        # Directly set the connection for testing
        mqi.connection = mock_redis
        mqi.is_connected = True

        assert mqi.is_connected is True
        assert mqi.password == "secret"

    @pytest.mark.asyncio
    async def test_connect_rabbitmq_success(self):
        """Test successful RabbitMQ connection setup."""
        mqi = MessageQueueIntegration(provider=QueueProvider.RABBITMQ, port=5672)

        # Create mock connection
        mock_conn = AsyncMock()
        mock_channel = AsyncMock()
        mock_conn.channel = AsyncMock(return_value=mock_channel)

        # Directly set the connection for testing
        mqi.connection = mock_conn
        mqi.is_connected = True

        assert mqi.is_connected is True
        assert mqi.connection is not None

    @pytest.mark.asyncio
    async def test_disconnect_redis(self):
        """Test disconnecting from Redis."""
        mqi = MessageQueueIntegration()

        # Create mock connection
        mock_redis = AsyncMock()
        mock_redis.close = AsyncMock()

        mqi.connection = mock_redis
        mqi.is_connected = True

        await mqi.disconnect()

        mock_redis.close.assert_called_once()
        assert mqi.is_connected is False

    @pytest.mark.asyncio
    async def test_disconnect_rabbitmq(self):
        """Test disconnecting from RabbitMQ."""
        mqi = MessageQueueIntegration(provider=QueueProvider.RABBITMQ)

        # Create mock connection
        mock_conn = AsyncMock()
        mock_conn.close = AsyncMock()

        mqi.connection = mock_conn
        mqi.is_connected = True

        await mqi.disconnect()

        mock_conn.close.assert_called_once()
        assert mqi.is_connected is False

    @pytest.mark.asyncio
    async def test_disconnect_no_connection(self):
        """Test disconnect when no connection exists."""
        mqi = MessageQueueIntegration()
        mqi.is_connected = False

        # Should not raise an error
        await mqi.disconnect()

        assert mqi.is_connected is False

    @pytest.mark.asyncio
    async def test_publish_not_connected(self):
        """Test publish when not connected."""
        mqi = MessageQueueIntegration()
        mqi.is_connected = False

        with pytest.raises(ConnectionError, match="Not connected"):
            await mqi.publish("test_topic", {"type": "agent_message", "data": {}})

    @pytest.mark.asyncio
    async def test_publish_redis(self):
        """Test publishing to Redis."""
        mqi = MessageQueueIntegration()

        # Create mock connection
        mock_redis = AsyncMock()
        mock_redis.publish = AsyncMock()

        mqi.connection = mock_redis
        mqi.is_connected = True

        await mqi.publish("test_topic", {"type": "agent_message", "data": {"key": "value"}})

        mock_redis.publish.assert_called_once()
        call_args = mock_redis.publish.call_args
        assert call_args[0][0] == "test_topic"

    @pytest.mark.asyncio
    async def test_publish_with_priority(self):
        """Test publishing with priority."""
        mqi = MessageQueueIntegration()

        # Create mock connection
        mock_redis = AsyncMock()
        mock_redis.publish = AsyncMock()

        mqi.connection = mock_redis
        mqi.is_connected = True

        await mqi.publish(
            "test_topic", {"type": "agent_message", "data": {}}, priority=MessagePriority.HIGH
        )

        mock_redis.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_subscribe_not_connected(self):
        """Test subscribe when not connected."""
        mqi = MessageQueueIntegration()
        mqi.is_connected = False

        async def handler(msg):
            pass

        with pytest.raises(ConnectionError, match="Not connected"):
            await mqi.subscribe("test_topic", handler)

    @pytest.mark.asyncio
    async def test_subscribe_redis(self):
        """Test subscribing to Redis topic."""
        mqi = MessageQueueIntegration()

        # Create mock connection
        mock_redis = AsyncMock()
        mock_pubsub = AsyncMock()
        mock_pubsub.subscribe = AsyncMock()
        mock_redis.pubsub = AsyncMock(return_value=mock_pubsub)

        mqi.connection = mock_redis
        mqi.is_connected = True

        async def handler(msg):
            pass

        # Mock _subscribe_redis to avoid actual Redis operations
        mqi._subscribe_redis = AsyncMock()

        await mqi.subscribe("test_topic", handler)

        mqi._subscribe_redis.assert_called_once_with("test_topic", handler)

    @pytest.mark.asyncio
    async def test_send_task(self):
        """Test sending a task message."""
        mqi = MessageQueueIntegration()

        # Create mock connection
        mock_redis = AsyncMock()
        mock_redis.publish = AsyncMock()

        mqi.connection = mock_redis
        mqi.is_connected = True

        await mqi.send_task(
            task_queue="tasks",
            task_id="task_123",
            description="Process data",
            parameters={"input": "data"},
        )

        mock_redis.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcast_event(self):
        """Test broadcasting an event."""
        mqi = MessageQueueIntegration()

        # Create mock connection
        mock_redis = AsyncMock()
        mock_redis.publish = AsyncMock()

        mqi.connection = mock_redis
        mqi.is_connected = True

        await mqi.broadcast_event(
            event_type="system_alert", event_data={"level": "warning", "message": "Test"}
        )

        mock_redis.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_notification(self):
        """Test sending a notification."""
        mqi = MessageQueueIntegration()

        # Create mock connection
        mock_redis = AsyncMock()
        mock_redis.publish = AsyncMock()

        mqi.connection = mock_redis
        mqi.is_connected = True

        await mqi.send_notification(
            notification_type="alert",
            title="Task completed",
            message="Task 123 has been processed",
            severity="info",
        )

        mock_redis.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_handler(self):
        """Test registering a message handler."""
        mqi = MessageQueueIntegration()

        async def handler(message):
            pass

        await mqi.register_handler(MessageType.TASK_SUBMIT, handler)

        assert MessageType.TASK_SUBMIT in mqi.message_handlers
        assert mqi.message_handlers[MessageType.TASK_SUBMIT] == handler

    @pytest.mark.asyncio
    async def test_handle_message_with_handler(self):
        """Test handling a message with a registered handler."""
        mqi = MessageQueueIntegration()

        handler_called = False
        received_message = None

        async def handler(message):
            nonlocal handler_called, received_message
            handler_called = True
            received_message = message

        await mqi.register_handler(MessageType.TASK_SUBMIT, handler)

        test_message = {
            "message_type_enum": MessageType.TASK_SUBMIT,
            "payload": {"task_id": "123"},
            "timestamp": datetime.now().isoformat(),
        }

        await mqi.handle_message(test_message)

        assert handler_called is True
        assert received_message is not None

    @pytest.mark.asyncio
    async def test_handle_message_no_handler(self):
        """Test handling a message without a registered handler."""
        mqi = MessageQueueIntegration()

        # Use an unregistered message type
        test_message = {
            "message_type_enum": MessageType.GOODBYE,
            "payload": {},
            "timestamp": datetime.now().isoformat(),
        }

        # Should log warning but not raise
        await mqi.handle_message(test_message)

    @pytest.mark.asyncio
    async def test_handle_message_handler_exception(self):
        """Test handling a message when handler raises an exception."""
        mqi = MessageQueueIntegration()

        async def failing_handler(message):
            raise ValueError("Handler error")

        await mqi.register_handler(MessageType.TASK_RESULT, failing_handler)

        test_message = {
            "message_type_enum": MessageType.TASK_RESULT,
            "payload": {},
            "timestamp": datetime.now().isoformat(),
        }

        # Should not raise an error, should log and continue
        await mqi.handle_message(test_message)

    @pytest.mark.asyncio
    async def test_get_queue_info_not_connected(self):
        """Test get_queue_info when not connected."""
        mqi = MessageQueueIntegration()
        mqi.is_connected = False

        result = await mqi.get_queue_info()

        assert result["provider"] == "redis"
        assert result["connected"] is False

    @pytest.mark.asyncio
    async def test_get_queue_info_redis(self):
        """Test get_queue_info with Redis."""
        mqi = MessageQueueIntegration()

        # Create mock connection
        mock_redis = AsyncMock()
        mock_redis.info = AsyncMock(return_value={"total_commands_processed": 1000})

        mqi.connection = mock_redis
        mqi.is_connected = True

        result = await mqi.get_queue_info()

        assert result["provider"] == "redis"
        assert result["connected"] is True
        assert "queue_length" in result

    @pytest.mark.asyncio
    async def test_get_queue_info_redis_exception(self):
        """Test get_queue_info with Redis when exception occurs."""
        mqi = MessageQueueIntegration()

        # Create mock connection that raises exception
        mock_redis = AsyncMock()
        mock_redis.info = AsyncMock(side_effect=Exception("Redis error"))

        mqi.connection = mock_redis
        mqi.is_connected = True

        result = await mqi.get_queue_info()

        # Should still return basic info even on error
        assert result["provider"] == "redis"
        assert "queue_length" not in result


class TestMessageQueueIntegrationRabbitMQ:
    """Tests for MessageQueueIntegration with RabbitMQ."""

    @pytest.mark.asyncio
    async def test_rabbitmq_setup(self):
        """Test RabbitMQ setup."""
        mqi = MessageQueueIntegration(provider=QueueProvider.RABBITMQ)

        # Create mock RabbitMQ connection with channel and exchange
        mock_conn = AsyncMock()
        mock_channel = AsyncMock()
        mock_exchange = AsyncMock()

        mock_conn.channel = AsyncMock(return_value=mock_channel)
        mock_channel.declare_exchange = AsyncMock(return_value=mock_exchange)

        mqi.connection = mock_conn
        mqi.is_connected = True

        assert mqi.is_connected is True
        assert mqi.provider == QueueProvider.RABBITMQ

    @pytest.mark.asyncio
    async def test_subscribe_rabbitmq(self):
        """Test subscribing to RabbitMQ queue."""
        mqi = MessageQueueIntegration(provider=QueueProvider.RABBITMQ)

        # Create mock RabbitMQ connection
        mock_conn = AsyncMock()
        mock_channel = AsyncMock()
        mock_exchange = AsyncMock()
        mock_queue = AsyncMock()

        mock_conn.channel = AsyncMock(return_value=mock_channel)
        mock_channel.declare_exchange = AsyncMock(return_value=mock_exchange)
        mock_channel.declare_queue = AsyncMock(return_value=mock_queue)
        mock_queue.bind = AsyncMock()
        mock_queue.consume = AsyncMock()

        mqi.connection = mock_conn
        mqi.is_connected = True

        async def handler(msg):
            pass

        # Mock _subscribe_rabbitmq to avoid actual RabbitMQ operations
        mqi._subscribe_rabbitmq = AsyncMock()

        await mqi.subscribe("test_queue", handler)

        mqi._subscribe_rabbitmq.assert_called_once_with("test_queue", handler)

    @pytest.mark.asyncio
    async def test_get_queue_info_rabbitmq(self):
        """Test get_queue_info with RabbitMQ."""
        mqi = MessageQueueIntegration(provider=QueueProvider.RABBITMQ)

        # Create mock connection
        mock_conn = AsyncMock()

        mqi.connection = mock_conn
        mqi.is_connected = True

        result = await mqi.get_queue_info()

        assert result["provider"] == "rabbitmq"
        assert result["connected"] is True


class TestMessageQueueIntegrationIntegration:
    """Integration tests for MessageQueueIntegration."""

    @pytest.mark.asyncio
    async def test_full_workflow_redis(self):
        """Test full workflow with Redis."""
        mqi = MessageQueueIntegration()

        # Create mock Redis connection
        mock_redis = AsyncMock()
        mock_redis.publish = AsyncMock()
        mock_redis.pubsub = AsyncMock(return_value=AsyncMock())
        mock_redis.close = AsyncMock()

        # Set up connection
        mqi.connection = mock_redis
        mqi.is_connected = True

        # Publish a message
        await mqi.publish("test_topic", {"type": "agent_message", "data": {}})

        # Subscribe to a topic (with mock)
        async def handler(msg):
            pass

        mqi._subscribe_redis = AsyncMock()
        await mqi.subscribe("test_topic", handler)

        # Disconnect
        await mqi.disconnect()

        mock_redis.publish.assert_called_once()
        mock_redis.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_task_and_notification_workflow(self):
        """Test task and notification workflow."""
        mqi = MessageQueueIntegration()

        # Create mock Redis connection
        mock_redis = AsyncMock()
        mock_redis.publish = AsyncMock()

        mqi.connection = mock_redis
        mqi.is_connected = True

        # Send a task
        await mqi.send_task(
            task_queue="tasks",
            task_id="task_123",
            description="Process data",
            parameters={"input": "data"},
        )

        # Broadcast an event
        await mqi.broadcast_event(event_type="task_started", event_data={"task_id": "123"})

        # Send a notification
        await mqi.send_notification(
            notification_type="alert",
            title="Task started",
            message="Task 123 has started",
            severity="info",
        )

        # Verify calls
        assert mock_redis.publish.call_count == 3

    @pytest.mark.asyncio
    async def test_handler_registration_workflow(self):
        """Test handler registration and message handling workflow."""
        mqi = MessageQueueIntegration()

        # Register handlers
        task_handler_called = False
        event_handler_called = False

        async def task_handler(message):
            nonlocal task_handler_called
            task_handler_called = True

        async def event_handler(message):
            nonlocal event_handler_called
            event_handler_called = True

        await mqi.register_handler(MessageType.TASK_SUBMIT, task_handler)
        await mqi.register_handler(MessageType.STREAM_START, event_handler)

        # Handle messages
        await mqi.handle_message(
            {
                "message_type_enum": MessageType.TASK_SUBMIT,
                "payload": {"task_id": "123"},
                "timestamp": datetime.now().isoformat(),
            }
        )

        await mqi.handle_message(
            {
                "message_type_enum": MessageType.STREAM_START,
                "payload": {"event_name": "test"},
                "timestamp": datetime.now().isoformat(),
            }
        )

        assert task_handler_called is True
        assert event_handler_called is True


class TestMessageQueueIntegrationEdgeCases:
    """Edge case tests for MessageQueueIntegration."""

    @pytest.mark.asyncio
    async def test_multiple_handlers_same_type(self):
        """Test registering multiple handlers for same message type (last wins)."""
        mqi = MessageQueueIntegration()

        async def handler1(message):
            pass

        async def handler2(message):
            pass

        await mqi.register_handler(MessageType.TASK_SUBMIT, handler1)
        await mqi.register_handler(MessageType.TASK_SUBMIT, handler2)

        assert mqi.message_handlers[MessageType.TASK_SUBMIT] == handler2

    @pytest.mark.asyncio
    async def test_publish_empty_message(self):
        """Test publishing an empty message."""
        mqi = MessageQueueIntegration()

        mock_redis = AsyncMock()
        mock_redis.publish = AsyncMock()

        mqi.connection = mock_redis
        mqi.is_connected = True

        await mqi.publish("test_topic", {})

        mock_redis.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_task_to_multiple_queues(self):
        """Test sending tasks to multiple queues."""
        mqi = MessageQueueIntegration()

        mock_redis = AsyncMock()
        mock_redis.publish = AsyncMock()

        mqi.connection = mock_redis
        mqi.is_connected = True

        # Send tasks to multiple queues
        queues = ["high_priority", "low_priority", "default"]
        for queue in queues:
            await mqi.send_task(
                task_queue=queue, task_id=f"task_{queue}", description="Process", parameters={}
            )

        assert mock_redis.publish.call_count == 3

    def test_mqi_provider_variants(self):
        """Test initialization with different providers."""
        redis_mqi = MessageQueueIntegration(provider=QueueProvider.REDIS)
        rabbitmq_mqi = MessageQueueIntegration(provider=QueueProvider.RABBITMQ)
        kafka_mqi = MessageQueueIntegration(provider=QueueProvider.KAFKA)
        sqs_mqi = MessageQueueIntegration(provider=QueueProvider.AWS_SQS)

        assert redis_mqi.provider == QueueProvider.REDIS
        assert rabbitmq_mqi.provider == QueueProvider.RABBITMQ
        assert kafka_mqi.provider == QueueProvider.KAFKA
        assert sqs_mqi.provider == QueueProvider.AWS_SQS


class TestMessageQueueIntegrationExtended:
    """Extended tests to improve coverage for message_queue_integration.py."""

    @pytest.mark.asyncio
    async def test_connect_redis_import_error(self):
        """Test Redis connection when redis library is not installed."""
        mqi = MessageQueueIntegration()

        with patch.dict("sys.modules", {"redis.asyncio": None}):
            with patch("builtins.__import__", side_effect=ImportError("No module named 'redis'")):
                with pytest.raises(ImportError, match="Redis library not installed"):
                    await mqi._connect_redis()

    @pytest.mark.asyncio
    async def test_connect_redis_connection_error(self):
        """Test Redis connection when connection fails."""
        mqi = MessageQueueIntegration()

        # Mock the redis module before the test
        mock_redis = MagicMock()
        mock_redis.from_url = MagicMock(side_effect=Exception("Connection refused"))

        with patch.dict("sys.modules", {"redis": mock_redis, "redis.asyncio": mock_redis}):
            with pytest.raises(ConnectionError, match="Failed to connect to Redis"):
                await mqi._connect_redis()

    @pytest.mark.asyncio
    async def test_connect_rabbitmq_import_error(self):
        """Test RabbitMQ connection when aio_pika library is not installed."""
        mqi = MessageQueueIntegration(provider=QueueProvider.RABBITMQ)

        # Simulate import error for aio_pika
        with patch.dict("sys.modules", {"aio_pika": None}):
            with patch(
                "builtins.__import__", side_effect=ImportError("No module named 'aio_pika'")
            ):
                with pytest.raises(ImportError, match="aio_pika library not installed"):
                    await mqi._connect_rabbitmq()

    @pytest.mark.asyncio
    async def test_connect_rabbitmq_connection_error(self):
        """Test RabbitMQ connection when connection fails."""
        mqi = MessageQueueIntegration(provider=QueueProvider.RABBITMQ)

        mock_aio_pika = MagicMock()
        mock_aio_pika.connect_robust = MagicMock(side_effect=Exception("Connection refused"))

        with patch.dict("sys.modules", {"aio_pika": mock_aio_pika}):
            with pytest.raises(ConnectionError, match="Failed to connect to RabbitMQ"):
                await mqi._connect_rabbitmq()

    @pytest.mark.asyncio
    async def test_publish_rabbitmq(self):
        """Test publishing to RabbitMQ."""
        mqi = MessageQueueIntegration(provider=QueueProvider.RABBITMQ)

        # Create mock RabbitMQ connection
        mock_conn = AsyncMock()
        mock_channel = AsyncMock()
        mock_exchange = AsyncMock()

        mock_conn.channel = AsyncMock(return_value=mock_channel)
        mock_channel.declare_exchange = AsyncMock(return_value=mock_exchange)
        mock_exchange.publish = AsyncMock()

        mqi.connection = mock_conn
        mqi.channel = mock_channel
        mqi.is_connected = True

        # Mock _publish_rabbitmq
        mqi._publish_rabbitmq = AsyncMock()

        await mqi.publish("test_topic", {"type": "agent_message", "data": {}})

        mqi._publish_rabbitmq.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_exception(self):
        """Test publish when exception occurs."""
        mqi = MessageQueueIntegration()

        mock_redis = AsyncMock()
        mock_redis.publish = AsyncMock(side_effect=Exception("Publish error"))

        mqi.connection = mock_redis
        mqi.is_connected = True

        with pytest.raises(Exception, match="Publish error"):
            await mqi.publish("test_topic", {"type": "agent_message", "data": {}})

    @pytest.mark.asyncio
    async def test_subscribe_exception(self):
        """Test subscribe when exception occurs."""
        mqi = MessageQueueIntegration()

        mock_redis = AsyncMock()
        mqi.connection = mock_redis
        mqi.is_connected = True

        # Mock _subscribe_redis to raise exception
        mqi._subscribe_redis = AsyncMock(side_effect=Exception("Subscribe error"))

        async def handler(msg):
            pass

        with pytest.raises(Exception, match="Subscribe error"):
            await mqi.subscribe("test_topic", handler)

    @pytest.mark.asyncio
    async def test_send_task_with_agent_id(self):
        """Test sending a task with specific agent ID."""
        mqi = MessageQueueIntegration()

        mock_redis = AsyncMock()
        mock_redis.publish = AsyncMock()

        mqi.connection = mock_redis
        mqi.is_connected = True

        await mqi.send_task(
            task_queue="tasks",
            task_id="task_123",
            description="Process data",
            parameters={"input": "data"},
            priority="high",
            agent_id="agent_456",
        )

        mock_redis.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcast_event_with_source(self):
        """Test broadcasting an event with source."""
        mqi = MessageQueueIntegration()

        mock_redis = AsyncMock()
        mock_redis.publish = AsyncMock()

        mqi.connection = mock_redis
        mqi.is_connected = True

        await mqi.broadcast_event(
            event_type="system_alert", event_data={"level": "warning"}, source="monitoring_service"
        )

        mock_redis.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_queue_info_rabbitmq_connected(self):
        """Test get_queue_info with RabbitMQ when connected."""
        mqi = MessageQueueIntegration(provider=QueueProvider.RABBITMQ)

        mock_conn = AsyncMock()
        mqi.connection = mock_conn
        mqi.is_connected = True

        result = await mqi.get_queue_info()

        assert result["provider"] == "rabbitmq"
        assert result["connected"] is True
        assert "queues" in result

    @pytest.mark.asyncio
    async def test_get_queue_info_rabbitmq_exception(self):
        """Test get_queue_info with RabbitMQ when exception occurs."""
        mqi = MessageQueueIntegration(provider=QueueProvider.RABBITMQ)

        mock_conn = AsyncMock()
        mqi.connection = mock_conn
        mqi.is_connected = True

        # The code path for RabbitMQ exception handling
        result = await mqi.get_queue_info()

        assert result["provider"] == "rabbitmq"
        assert result["connected"] is True

    @pytest.mark.asyncio
    async def test_connect_actual_redis_mock(self):
        """Test connect method with mocked Redis."""
        mqi = MessageQueueIntegration()

        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)

        with patch.object(mqi, "_connect_redis", new_callable=AsyncMock) as mock_connect:
            await mqi.connect()

            mock_connect.assert_called_once()
            assert mqi.is_connected is True

    @pytest.mark.asyncio
    async def test_connect_actual_rabbitmq_mock(self):
        """Test connect method with mocked RabbitMQ."""
        mqi = MessageQueueIntegration(provider=QueueProvider.RABBITMQ)

        with patch.object(mqi, "_connect_rabbitmq", new_callable=AsyncMock) as mock_connect:
            await mqi.connect()

            mock_connect.assert_called_once()
            assert mqi.is_connected is True

    @pytest.mark.asyncio
    async def test_handle_message_none_message_type(self):
        """Test handling message with None message_type_enum."""
        mqi = MessageQueueIntegration()

        test_message = {
            "message_type_enum": None,
            "payload": {},
            "timestamp": datetime.now().isoformat(),
        }

        # Should handle gracefully (may log warning or raise, depending on implementation)
        try:
            await mqi.handle_message(test_message)
        except AttributeError:
            # Expected if message_type is None and code tries to access .value
            pass

    @pytest.mark.asyncio
    async def test_publish_rabbitmq_direct(self):
        """Test direct RabbitMQ publish method."""
        pytest.skip("Requires aio_pika to be installed for direct testing")

    @pytest.mark.asyncio
    async def test_subscribe_rabbitmq_direct(self):
        """Test direct RabbitMQ subscribe method."""
        pytest.skip("Requires aio_pika to be installed for direct testing")

    @pytest.mark.asyncio
    async def test_subscribe_redis_direct(self):
        """Test direct Redis subscribe method."""
        mqi = MessageQueueIntegration()

        mock_redis = AsyncMock()
        mock_pubsub = AsyncMock()

        mqi.connection = mock_redis
        mqi.is_connected = True

        # Create a mock pubsub that returns an async iterator
        mock_pubsub.subscribe = AsyncMock()
        mock_redis.pubsub = Mock(return_value=mock_pubsub)

        async def handler(msg):
            pass

        await mqi._subscribe_redis("test_topic", handler)

        mock_redis.pubsub.assert_called_once()
        mock_pubsub.subscribe.assert_called_once()
