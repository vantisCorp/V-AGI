"""
Tests for Message Queue Integration
Tests Redis and RabbitMQ message queue functionality
"""
import pytest
import sys
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import asyncio
import json

from src.api.message_queue_integration import (
    MessageQueueIntegration,
    QueueProvider
)
from src.api.communication_protocol import MessageType, MessagePriority


class TestMessageQueueIntegration:
    """Tests for MessageQueueIntegration class."""
    
    def test_init_default_values(self):
        """Test initialization with default values."""
        mq = MessageQueueIntegration()
        
        assert mq.provider == QueueProvider.REDIS
        assert mq.host == "localhost"
        assert mq.port == 6379
        assert mq.username is None
        assert mq.password is None
        assert mq.connection is None
        assert mq.is_connected is False
        assert mq.message_handlers == {}
    
    def test_init_custom_values(self):
        """Test initialization with custom values."""
        mq = MessageQueueIntegration(
            provider=QueueProvider.RABBITMQ,
            host="custom-host",
            port=5672,
            username="admin",
            password="secret"
        )
        
        assert mq.provider == QueueProvider.RABBITMQ
        assert mq.host == "custom-host"
        assert mq.port == 5672
        assert mq.username == "admin"
        assert mq.password == "secret"
    
    def test_queue_provider_enum(self):
        """Test QueueProvider enum values."""
        assert QueueProvider.REDIS.value == "redis"
        assert QueueProvider.RABBITMQ.value == "rabbitmq"
        assert QueueProvider.KAFKA.value == "kafka"
        assert QueueProvider.AWS_SQS.value == "aws_sqs"
    
    @pytest.mark.asyncio
    async def test_connect_redis_success(self):
        """Test successful Redis connection."""
        mq = MessageQueueIntegration(provider=QueueProvider.REDIS)
        
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        
        # Mock the redis module
        mock_redis_module = MagicMock()
        mock_redis_async = MagicMock()
        mock_redis_async.from_url = AsyncMock(return_value=mock_redis)
        mock_redis_module.asyncio = mock_redis_async
        
        with patch.dict(sys.modules, {'redis': mock_redis_module, 'redis.asyncio': mock_redis_async}):
            await mq.connect()
            
            assert mq.is_connected is True
            assert mq.connection is not None
    
    @pytest.mark.asyncio
    async def test_connect_rabbitmq_success(self):
        """Test successful RabbitMQ connection."""
        mq = MessageQueueIntegration(
            provider=QueueProvider.RABBITMQ,
            port=5672
        )
        
        mock_connection = AsyncMock()
        mock_channel = AsyncMock()
        mock_connection.channel = AsyncMock(return_value=mock_channel)
        
        mock_aio_pika = MagicMock()
        mock_aio_pika.connect_robust = AsyncMock(return_value=mock_connection)
        
        with patch.dict(sys.modules, {'aio_pika': mock_aio_pika}):
            await mq.connect()
            
            assert mq.is_connected is True
            assert mq.connection is not None
    
    @pytest.mark.asyncio
    async def test_connect_unsupported_provider(self):
        """Test connection with unsupported provider."""
        mq = MessageQueueIntegration(provider=QueueProvider.KAFKA)
        
        with pytest.raises(ValueError, match="Unsupported provider"):
            await mq.connect()
    
    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test disconnection."""
        mq = MessageQueueIntegration()
        mq.is_connected = True
        mq.connection = AsyncMock()
        mq.connection.close = AsyncMock()
        
        await mq.disconnect()
        
        assert mq.is_connected is False
        mq.connection.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_disconnect_not_connected(self):
        """Test disconnection when not connected."""
        mq = MessageQueueIntegration()
        
        # Should not raise error
        await mq.disconnect()
        
        assert mq.is_connected is False
    
    @pytest.mark.asyncio
    async def test_publish_not_connected(self):
        """Test publishing when not connected."""
        mq = MessageQueueIntegration()
        
        with pytest.raises(ConnectionError, match="Not connected"):
            await mq.publish("test_topic", {"data": "test"})
    
    @pytest.mark.asyncio
    async def test_subscribe_not_connected(self):
        """Test subscribing when not connected."""
        mq = MessageQueueIntegration()
        
        async def handler(msg):
            pass
        
        with pytest.raises(ConnectionError, match="Not connected"):
            await mq.subscribe("test_topic", handler)
    
    @pytest.mark.asyncio
    async def test_publish_redis(self):
        """Test publishing to Redis."""
        mq = MessageQueueIntegration(provider=QueueProvider.REDIS)
        mq.is_connected = True
        mq.connection = AsyncMock()
        mq.connection.publish = AsyncMock()
        
        await mq.publish("test_topic", {"data": "test"}, MessagePriority.MEDIUM)
        
        mq.connection.publish.assert_called_once()
    
    @pytest.mark.skip(reason="Requires aio_pika library to be installed")
    @pytest.mark.asyncio
    async def test_publish_rabbitmq(self):
        """Test publishing to RabbitMQ - requires aio_pika library."""
        pass
    
    @pytest.mark.asyncio
    async def test_register_handler(self):
        """Test registering message handler."""
        mq = MessageQueueIntegration()
        
        async def handler(msg):
            pass
        
        await mq.register_handler(MessageType.TASK_SUBMIT, handler)
        
        assert MessageType.TASK_SUBMIT in mq.message_handlers
        assert mq.message_handlers[MessageType.TASK_SUBMIT] == handler
    
    @pytest.mark.asyncio
    async def test_send_task(self):
        """Test sending task to queue."""
        mq = MessageQueueIntegration(provider=QueueProvider.REDIS)
        mq.is_connected = True
        mq.connection = AsyncMock()
        mq.connection.publish = AsyncMock()
        
        await mq.send_task(
            task_queue="tasks",
            task_id="task-123",
            description="Test task",
            parameters={"param": "value"},
            priority="high"
        )
        
        mq.connection.publish.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_broadcast_event(self):
        """Test broadcasting event."""
        mq = MessageQueueIntegration(provider=QueueProvider.REDIS)
        mq.is_connected = True
        mq.connection = AsyncMock()
        mq.connection.publish = AsyncMock()
        
        await mq.broadcast_event(
            event_type="task_completed",
            event_data={"task_id": "task-123"},
            source="agent-1"
        )
        
        mq.connection.publish.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_notification(self):
        """Test sending notification."""
        mq = MessageQueueIntegration(provider=QueueProvider.REDIS)
        mq.is_connected = True
        mq.connection = AsyncMock()
        mq.connection.publish = AsyncMock()
        
        await mq.send_notification(
            notification_type="alert",
            title="Test Alert",
            message="This is a test notification",
            severity="warning"
        )
        
        mq.connection.publish.assert_called_once()


class TestMessageQueueProviderSpecific:
    """Tests for provider-specific functionality."""
    
    @pytest.mark.asyncio
    async def test_redis_with_password(self):
        """Test Redis connection with password."""
        mq = MessageQueueIntegration(
            provider=QueueProvider.REDIS,
            password="secret"
        )
        
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        
        # Mock the redis module
        mock_redis_module = MagicMock()
        mock_redis_async = MagicMock()
        mock_redis_async.from_url = AsyncMock(return_value=mock_redis)
        mock_redis_module.asyncio = mock_redis_async
        
        with patch.dict(sys.modules, {'redis': mock_redis_module, 'redis.asyncio': mock_redis_async}):
            await mq.connect()
            
            assert mq.is_connected is True
    
    @pytest.mark.asyncio
    async def test_rabbitmq_with_credentials(self):
        """Test RabbitMQ connection with credentials."""
        mq = MessageQueueIntegration(
            provider=QueueProvider.RABBITMQ,
            username="admin",
            password="secret",
            port=5672
        )
        
        mock_connection = AsyncMock()
        mock_channel = AsyncMock()
        mock_connection.channel = AsyncMock(return_value=mock_channel)
        
        mock_aio_pika = MagicMock()
        mock_aio_pika.connect_robust = AsyncMock(return_value=mock_connection)
        
        with patch.dict(sys.modules, {'aio_pika': mock_aio_pika}):
            await mq.connect()
            
            assert mq.is_connected is True