"""
Tests for Communication Protocol
Tests message formats, parsing, validation, and queue management
"""

import json
from datetime import datetime
from unittest.mock import patch

import pytest

from src.api.communication_protocol import (MessagePriority, MessageProtocol,
                                            MessageQueue, MessageType)


class TestMessageType:
    """Tests for MessageType enum."""

    def test_message_type_values(self):
        """Test MessageType enum values."""
        assert MessageType.WELCOME.value == "welcome"
        assert MessageType.PING.value == "ping"
        assert MessageType.PONG.value == "pong"
        assert MessageType.TASK_SUBMIT.value == "task_submit"
        assert MessageType.TACK.value == "task_ack"
        assert MessageType.ERROR.value == "error"
        assert MessageType.EVENT.value == "event"
        assert MessageType.NOTIFICATION.value == "notification"
        assert MessageType.AGENT_MESSAGE.value == "agent_message"

    def test_message_type_count(self):
        """Test that all expected message types exist."""
        # Connection management
        assert MessageType.WELCOME in MessageType
        assert MessageType.PING in MessageType
        assert MessageType.PONG in MessageType
        assert MessageType.GOODBYE in MessageType

        # Task management
        assert MessageType.TASK_SUBMIT in MessageType
        assert MessageType.TACK in MessageType
        assert MessageType.TASK_RESULT in MessageType
        assert MessageType.TASK_CANCEL in MessageType
        assert MessageType.TASK_STATUS in MessageType

        # Agent management
        assert MessageType.AGENT_LIST in MessageType
        assert MessageType.AGENT_STATUS in MessageType

        # Streaming
        assert MessageType.STREAM_START in MessageType
        assert MessageType.STREAM_STARTED in MessageType
        assert MessageType.STREAM_DATA in MessageType
        assert MessageType.STREAM_STOP in MessageType
        assert MessageType.STREAM_STOPPED in MessageType

        # Subscriptions
        assert MessageType.SUBSCRIBE in MessageType
        assert MessageType.SUBSCRIPTION_CONFIRMED in MessageType
        assert MessageType.UNSUBSCRIBE in MessageType
        assert MessageType.SUBSCRIPTION_CANCELLED in MessageType


class TestMessagePriority:
    """Tests for MessagePriority enum."""

    def test_priority_values(self):
        """Test MessagePriority enum values."""
        assert MessagePriority.LOW.value == 0
        assert MessagePriority.MEDIUM.value == 1
        assert MessagePriority.HIGH.value == 2
        assert MessagePriority.CRITICAL.value == 3

    def test_priority_ordering(self):
        """Test that priorities are ordered correctly."""
        assert MessagePriority.LOW.value < MessagePriority.MEDIUM.value
        assert MessagePriority.MEDIUM.value < MessagePriority.HIGH.value
        assert MessagePriority.HIGH.value < MessagePriority.CRITICAL.value


class TestMessageProtocol:
    """Tests for MessageProtocol class."""

    @pytest.fixture
    def protocol(self):
        """Create a MessageProtocol instance."""
        return MessageProtocol()

    def test_protocol_version(self, protocol):
        """Test protocol version constant."""
        assert protocol.PROTOCOL_VERSION == "1.0.0"

    def test_init(self, protocol):
        """Test MessageProtocol initialization."""
        assert hasattr(protocol, "message_handlers")
        assert protocol.message_handlers == {}

    def test_create_message_basic(self, protocol):
        """Test basic message creation."""
        message_str = protocol.create_message(message_type=MessageType.PING, data={"test": "value"})

        message = json.loads(message_str)

        assert message["protocol_version"] == "1.0.0"
        assert message["type"] == "ping"
        assert message["data"] == {"test": "value"}
        assert "message_id" in message
        assert "timestamp" in message
        assert message["priority"] == MessagePriority.MEDIUM.value

    def test_create_message_with_custom_id(self, protocol):
        """Test message creation with custom message ID."""
        message_str = protocol.create_message(
            message_type=MessageType.PING, data={}, message_id="custom-id-123"
        )

        message = json.loads(message_str)
        assert message["message_id"] == "custom-id-123"

    def test_create_message_with_reply_to(self, protocol):
        """Test message creation with reply_to field."""
        message_str = protocol.create_message(
            message_type=MessageType.PONG, data={}, reply_to="original-msg-id"
        )

        message = json.loads(message_str)
        assert message["reply_to"] == "original-msg-id"

    def test_create_message_with_priority(self, protocol):
        """Test message creation with custom priority."""
        message_str = protocol.create_message(
            message_type=MessageType.ERROR,
            data={"error": "test"},
            priority=MessagePriority.CRITICAL,
        )

        message = json.loads(message_str)
        assert message["priority"] == MessagePriority.CRITICAL.value

    def test_create_message_no_data(self, protocol):
        """Test message creation without data."""
        message_str = protocol.create_message(message_type=MessageType.WELCOME)

        message = json.loads(message_str)
        assert message["data"] == {}


class TestMessageProtocolParsing:
    """Tests for message parsing."""

    @pytest.fixture
    def protocol(self):
        """Create a MessageProtocol instance."""
        return MessageProtocol()

    def test_parse_message_valid(self, protocol):
        """Test parsing a valid message."""
        raw_message = json.dumps(
            {
                "protocol_version": "1.0.0",
                "message_id": "msg-123",
                "type": "ping",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {"test": "value"},
            }
        )

        message = protocol.parse_message(raw_message)

        assert message["protocol_version"] == "1.0.0"
        assert message["message_id"] == "msg-123"
        assert message["type"] == "ping"
        assert message["message_type_enum"] == MessageType.PING

    def test_parse_message_missing_protocol_version(self, protocol):
        """Test parsing message with missing protocol_version."""
        raw_message = json.dumps(
            {"message_id": "msg-123", "type": "ping", "timestamp": datetime.utcnow().isoformat()}
        )

        with pytest.raises(ValueError, match="Missing required field: protocol_version"):
            protocol.parse_message(raw_message)

    def test_parse_message_missing_message_id(self, protocol):
        """Test parsing message with missing message_id."""
        raw_message = json.dumps(
            {
                "protocol_version": "1.0.0",
                "type": "ping",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        with pytest.raises(ValueError, match="Missing required field: message_id"):
            protocol.parse_message(raw_message)

    def test_parse_message_missing_type(self, protocol):
        """Test parsing message with missing type."""
        raw_message = json.dumps(
            {
                "protocol_version": "1.0.0",
                "message_id": "msg-123",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        with pytest.raises(ValueError, match="Missing required field: type"):
            protocol.parse_message(raw_message)

    def test_parse_message_missing_timestamp(self, protocol):
        """Test parsing message with missing timestamp."""
        raw_message = json.dumps(
            {"protocol_version": "1.0.0", "message_id": "msg-123", "type": "ping"}
        )

        with pytest.raises(ValueError, match="Missing required field: timestamp"):
            protocol.parse_message(raw_message)

    def test_parse_message_invalid_protocol_version(self, protocol):
        """Test parsing message with invalid protocol version."""
        raw_message = json.dumps(
            {
                "protocol_version": "2.0.0",
                "message_id": "msg-123",
                "type": "ping",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        with pytest.raises(ValueError, match="Unsupported protocol version"):
            protocol.parse_message(raw_message)

    def test_parse_message_invalid_json(self, protocol):
        """Test parsing invalid JSON."""
        with pytest.raises(json.JSONDecodeError):
            protocol.parse_message("not valid json")

    def test_parse_message_invalid_type(self, protocol):
        """Test parsing message with invalid message type."""
        raw_message = json.dumps(
            {
                "protocol_version": "1.0.0",
                "message_id": "msg-123",
                "type": "invalid_type",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        with pytest.raises(ValueError, match="Unknown message type"):
            protocol.parse_message(raw_message)


class TestMessageProtocolValidation:
    """Tests for message validation."""

    @pytest.fixture
    def protocol(self):
        """Create a MessageProtocol instance."""
        return MessageProtocol()

    def test_validate_message_valid(self, protocol):
        """Test validating a valid message."""
        message = {
            "protocol_version": "1.0.0",
            "message_id": "msg-123",
            "type": "ping",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {},
        }

        assert protocol.validate_message(message) is True

    def test_validate_message_missing_protocol_version(self, protocol):
        """Test validating message with missing protocol_version."""
        message = {
            "message_id": "msg-123",
            "type": "ping",
            "timestamp": datetime.utcnow().isoformat(),
        }

        assert protocol.validate_message(message) is False

    def test_validate_message_missing_message_id(self, protocol):
        """Test validating message with missing message_id."""
        message = {
            "protocol_version": "1.0.0",
            "type": "ping",
            "timestamp": datetime.utcnow().isoformat(),
        }

        assert protocol.validate_message(message) is False

    def test_validate_message_missing_type(self, protocol):
        """Test validating message with missing type."""
        message = {
            "protocol_version": "1.0.0",
            "message_id": "msg-123",
            "timestamp": datetime.utcnow().isoformat(),
        }

        assert protocol.validate_message(message) is False

    def test_validate_message_invalid_protocol_version(self, protocol):
        """Test validating message with wrong protocol version."""
        message = {
            "protocol_version": "2.0.0",
            "message_id": "msg-123",
            "type": "ping",
            "timestamp": datetime.utcnow().isoformat(),
        }

        assert protocol.validate_message(message) is False

    def test_validate_message_invalid_type(self, protocol):
        """Test validating message with invalid type."""
        message = {
            "protocol_version": "1.0.0",
            "message_id": "msg-123",
            "type": "invalid_type",
            "timestamp": datetime.utcnow().isoformat(),
        }

        assert protocol.validate_message(message) is False

    def test_validate_message_invalid_timestamp(self, protocol):
        """Test validating message with invalid timestamp."""
        message = {
            "protocol_version": "1.0.0",
            "message_id": "msg-123",
            "type": "ping",
            "timestamp": "not-a-timestamp",
        }

        assert protocol.validate_message(message) is False

    def test_validate_message_missing_timestamp(self, protocol):
        """Test validating message with missing timestamp."""
        message = {"protocol_version": "1.0.0", "message_id": "msg-123", "type": "ping"}

        assert protocol.validate_message(message) is False


class TestMessageProtocolSpecializedMessages:
    """Tests for specialized message creation methods."""

    @pytest.fixture
    def protocol(self):
        """Create a MessageProtocol instance."""
        return MessageProtocol()

    def test_create_error_message(self, protocol):
        """Test error message creation."""
        message_str = protocol.create_error_message(
            error="Test error",
            error_code="ERR001",
            details={"detail": "value"},
            reply_to="original-msg",
        )

        message = json.loads(message_str)

        assert message["type"] == "error"
        assert message["data"]["error"] == "Test error"
        assert message["data"]["error_code"] == "ERR001"
        assert message["data"]["details"] == {"detail": "value"}
        assert message["reply_to"] == "original-msg"
        assert message["priority"] == MessagePriority.HIGH.value

    def test_create_error_message_minimal(self, protocol):
        """Test error message creation with minimal args."""
        message_str = protocol.create_error_message(error="Simple error")

        message = json.loads(message_str)

        assert message["type"] == "error"
        assert message["data"]["error"] == "Simple error"
        assert message["data"]["error_code"] is None

    def test_create_task_message(self, protocol):
        """Test task message creation."""
        message_str = protocol.create_task_message(
            task_id="task-123",
            description="Test task",
            parameters={"key": "value"},
            priority="high",
            agent_id="agent-1",
        )

        message = json.loads(message_str)

        assert message["type"] == "task_submit"
        assert message["data"]["task_id"] == "task-123"
        assert message["data"]["description"] == "Test task"
        assert message["data"]["parameters"] == {"key": "value"}
        assert message["data"]["priority"] == "high"
        assert message["data"]["agent_id"] == "agent-1"

    def test_create_task_message_minimal(self, protocol):
        """Test task message creation with minimal args."""
        message_str = protocol.create_task_message(
            task_id="task-123", description="Test task", parameters={}
        )

        message = json.loads(message_str)

        assert message["data"]["priority"] == "medium"
        assert message["data"]["agent_id"] is None

    def test_create_agent_message(self, protocol):
        """Test agent message creation."""
        message_str = protocol.create_agent_message(
            from_agent="agent-1",
            to_agent="agent-2",
            message_content={"text": "Hello"},
            message_type="greeting",
        )

        message = json.loads(message_str)

        assert message["type"] == "agent_message"
        assert message["data"]["from_agent"] == "agent-1"
        assert message["data"]["to_agent"] == "agent-2"
        assert message["data"]["message_type"] == "greeting"
        assert message["data"]["content"] == {"text": "Hello"}

    def test_create_agent_message_default_type(self, protocol):
        """Test agent message creation with default type."""
        message_str = protocol.create_agent_message(
            from_agent="agent-1", to_agent="agent-2", message_content="Hello"
        )

        message = json.loads(message_str)
        assert message["data"]["message_type"] == "communication"

    def test_create_notification(self, protocol):
        """Test notification creation."""
        message_str = protocol.create_notification(
            notification_type="alert",
            title="Test Notification",
            message="This is a test",
            severity="warning",
        )

        message = json.loads(message_str)

        assert message["type"] == "notification"
        assert message["data"]["type"] == "alert"
        assert message["data"]["title"] == "Test Notification"
        assert message["data"]["message"] == "This is a test"
        assert message["data"]["severity"] == "warning"

    def test_create_notification_default_severity(self, protocol):
        """Test notification creation with default severity."""
        message_str = protocol.create_notification(
            notification_type="info", title="Test", message="Message"
        )

        message = json.loads(message_str)
        assert message["data"]["severity"] == "info"

    def test_create_event(self, protocol):
        """Test event creation."""
        message_str = protocol.create_event(
            event_type="system", event_data={"status": "started"}, source="main"
        )

        message = json.loads(message_str)

        assert message["type"] == "event"
        assert message["data"]["event_type"] == "system"
        assert message["data"]["data"] == {"status": "started"}
        assert message["data"]["source"] == "main"

    def test_create_event_no_source(self, protocol):
        """Test event creation without source."""
        message_str = protocol.create_event(event_type="system", event_data={"status": "started"})

        message = json.loads(message_str)
        assert message["data"]["source"] is None


class TestMessageProtocolHelpers:
    """Tests for message helper methods."""

    @pytest.fixture
    def protocol(self):
        """Create a MessageProtocol instance."""
        return MessageProtocol()

    def test_get_message_type_valid(self, protocol):
        """Test getting message type from valid message."""
        raw_message = json.dumps(
            {"type": "ping", "protocol_version": "1.0.0", "message_id": "msg-1"}
        )

        msg_type = protocol.get_message_type(raw_message)
        assert msg_type == MessageType.PING

    def test_get_message_type_no_type(self, protocol):
        """Test getting message type from message without type."""
        raw_message = json.dumps({"message_id": "msg-1"})

        msg_type = protocol.get_message_type(raw_message)
        assert msg_type is None

    def test_get_message_type_invalid_json(self, protocol):
        """Test getting message type from invalid JSON."""
        msg_type = protocol.get_message_type("not json")
        assert msg_type is None

    def test_get_message_type_invalid_type_value(self, protocol):
        """Test getting message type with invalid type value."""
        raw_message = json.dumps({"type": "invalid_type"})

        msg_type = protocol.get_message_type(raw_message)
        assert msg_type is None

    def test_is_error_message_true(self, protocol):
        """Test is_error_message returns True for error messages."""
        raw_message = json.dumps({"type": "error", "data": {"error": "test"}})

        assert protocol.is_error_message(raw_message) is True

    def test_is_error_message_false(self, protocol):
        """Test is_error_message returns False for non-error messages."""
        raw_message = json.dumps({"type": "ping"})

        assert protocol.is_error_message(raw_message) is False

    def test_is_task_message_true(self, protocol):
        """Test is_task_message returns True for task messages."""
        for msg_type in ["task_submit", "task_ack", "task_result", "task_cancel", "task_status"]:
            raw_message = json.dumps({"type": msg_type})
            assert protocol.is_task_message(raw_message) is True

    def test_is_task_message_false(self, protocol):
        """Test is_task_message returns False for non-task messages."""
        raw_message = json.dumps({"type": "ping"})
        assert protocol.is_task_message(raw_message) is False

    def test_extract_message_id_found(self, protocol):
        """Test extracting message ID from message."""
        raw_message = json.dumps({"message_id": "msg-123", "type": "ping"})

        msg_id = protocol.extract_message_id(raw_message)
        assert msg_id == "msg-123"

    def test_extract_message_id_not_found(self, protocol):
        """Test extracting message ID when not present."""
        raw_message = json.dumps({"type": "ping"})

        msg_id = protocol.extract_message_id(raw_message)
        assert msg_id is None

    def test_extract_message_id_invalid_json(self, protocol):
        """Test extracting message ID from invalid JSON."""
        msg_id = protocol.extract_message_id("not json")
        assert msg_id is None


class TestMessageQueue:
    """Tests for MessageQueue class."""

    @pytest.fixture
    def queue(self):
        """Create a MessageQueue instance."""
        return MessageQueue(max_size=100)

    def test_init(self, queue):
        """Test MessageQueue initialization."""
        assert queue.max_size == 100
        assert len(queue.queues) == len(MessagePriority)
        assert queue.size() == 0

    def test_enqueue_single_message(self, queue):
        """Test enqueuing a single message."""
        message = {"test": "value"}
        result = queue.enqueue(message, MessagePriority.MEDIUM)

        assert result is True
        assert queue.size() == 1

    def test_enqueue_max_size(self):
        """Test enqueuing messages up to max size."""
        queue = MessageQueue(max_size=3)

        assert queue.enqueue({"msg": 1}, MessagePriority.LOW) is True
        assert queue.enqueue({"msg": 2}, MessagePriority.LOW) is True
        assert queue.enqueue({"msg": 3}, MessagePriority.LOW) is True
        assert queue.enqueue({"msg": 4}, MessagePriority.LOW) is False  # Exceeds max

    def test_dequeue_empty_queue(self, queue):
        """Test dequeuing from empty queue."""
        result = queue.dequeue()
        assert result is None

    def test_dequeue_priority_order(self, queue):
        """Test that dequeue returns highest priority message first."""
        queue.enqueue({"priority": "low"}, MessagePriority.LOW)
        queue.enqueue({"priority": "critical"}, MessagePriority.CRITICAL)
        queue.enqueue({"priority": "medium"}, MessagePriority.MEDIUM)

        # Should get critical first
        msg = queue.dequeue()
        assert msg["priority"] == "critical"

        # Then medium
        msg = queue.dequeue()
        assert msg["priority"] == "medium"

        # Then low
        msg = queue.dequeue()
        assert msg["priority"] == "low"

    def test_dequeue_fifo_same_priority(self, queue):
        """Test FIFO order for same priority messages."""
        queue.enqueue({"order": 1}, MessagePriority.MEDIUM)
        queue.enqueue({"order": 2}, MessagePriority.MEDIUM)
        queue.enqueue({"order": 3}, MessagePriority.MEDIUM)

        assert queue.dequeue()["order"] == 1
        assert queue.dequeue()["order"] == 2
        assert queue.dequeue()["order"] == 3

    def test_peek_empty_queue(self, queue):
        """Test peeking at empty queue."""
        result = queue.peek()
        assert result is None

    def test_peek_returns_without_removing(self, queue):
        """Test that peek returns message without removing it."""
        queue.enqueue({"test": "value"}, MessagePriority.MEDIUM)

        msg = queue.peek()
        assert msg == {"test": "value"}
        assert queue.size() == 1  # Still in queue

    def test_peek_priority_order(self, queue):
        """Test that peek returns highest priority message."""
        queue.enqueue({"priority": "low"}, MessagePriority.LOW)
        queue.enqueue({"priority": "high"}, MessagePriority.HIGH)

        msg = queue.peek()
        assert msg["priority"] == "high"

    def test_size(self, queue):
        """Test queue size tracking."""
        assert queue.size() == 0

        queue.enqueue({"msg": 1}, MessagePriority.LOW)
        assert queue.size() == 1

        queue.enqueue({"msg": 2}, MessagePriority.MEDIUM)
        assert queue.size() == 2

        queue.dequeue()
        assert queue.size() == 1

    def test_clear(self, queue):
        """Test clearing the queue."""
        queue.enqueue({"msg": 1}, MessagePriority.LOW)
        queue.enqueue({"msg": 2}, MessagePriority.MEDIUM)
        queue.enqueue({"msg": 3}, MessagePriority.HIGH)

        queue.clear()

        assert queue.size() == 0
        for priority in MessagePriority:
            assert len(queue.queues[priority]) == 0
            assert queue.message_counts[priority] == 0

    def test_get_stats(self, queue):
        """Test getting queue statistics."""
        queue.enqueue({"msg": 1}, MessagePriority.LOW)
        queue.enqueue({"msg": 2}, MessagePriority.MEDIUM)
        queue.enqueue({"msg": 3}, MessagePriority.HIGH)

        stats = queue.get_stats()

        assert stats["total_messages"] == 3
        assert stats["max_size"] == 100
        assert "messages_by_priority" in stats
        assert "utilization" in stats
        assert stats["messages_by_priority"]["LOW"] == 1
        assert stats["messages_by_priority"]["MEDIUM"] == 1
        assert stats["messages_by_priority"]["HIGH"] == 1


class TestMessageQueuePriority:
    """Tests for MessageQueue priority handling."""

    @pytest.fixture
    def queue(self):
        """Create a MessageQueue instance."""
        return MessageQueue()

    def test_all_priorities(self, queue):
        """Test enqueuing and dequeuing all priority levels."""
        messages = {
            MessagePriority.LOW: {"level": "low"},
            MessagePriority.MEDIUM: {"level": "medium"},
            MessagePriority.HIGH: {"level": "high"},
            MessagePriority.CRITICAL: {"level": "critical"},
        }

        # Enqueue in random order
        for priority, msg in messages.items():
            queue.enqueue(msg, priority)

        # Dequeue should return in priority order
        assert queue.dequeue()["level"] == "critical"
        assert queue.dequeue()["level"] == "high"
        assert queue.dequeue()["level"] == "medium"
        assert queue.dequeue()["level"] == "low"

    def test_multiple_same_priority_queues(self, queue):
        """Test that multiple messages of same priority are handled correctly."""
        # Enqueue 5 LOW priority messages
        for i in range(5):
            queue.enqueue({"num": i}, MessagePriority.LOW)

        # All should be dequeued in FIFO order
        for i in range(5):
            msg = queue.dequeue()
            assert msg["num"] == i
