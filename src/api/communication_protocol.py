"""
OMNI-AI Communication Protocol
Defines message formats and protocols for agent communication
"""
import json
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class MessageType(Enum):
    """Message type enumeration."""
    
    # Connection Management
    WELCOME = "welcome"
    PING = "ping"
    PONG = "pong"
    GOODBYE = "goodbye"
    
    # Task Management
    TASK_SUBMIT = "task_submit"
    TACK = "task_ack"  # Task acknowledgment
    TASK_RESULT = "task_result"
    TASK_CANCEL = "task_cancel"
    TASK_STATUS = "task_status"
    
    # Agent Management
    AGENT_LIST = "agent_list"
    AGENT_STATUS = "agent_status"
    
    # Streaming
    STREAM_START = "stream_start"
    STREAM_STARTED = "stream_started"
    STREAM_DATA = "stream_data"
    STREAM_STOP = "stream_stop"
    STREAM_STOPPED = "stream_stopped"
    
    # Subscriptions
    SUBSCRIBE = "subscribe"
    SUBSCRIPTION_CONFIRMED = "subscription_confirmed"
    UNSUBSCRIBE = "unsubscribe"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"
    
    # Events
    EVENT = "event"
    NOTIFICATION = "notification"
    
    # Errors
    ERROR = "error"
    
    # Agent Communication
    AGENT_MESSAGE = "agent_message"
    AGENT_RESPONSE = "agent_response"


class MessagePriority(Enum):
    """Message priority enumeration."""
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3


class MessageProtocol:
    """
    Message protocol for OMNI-AI communication.
    Handles message creation, parsing, and validation.
    """
    
    PROTOCOL_VERSION = "1.0.0"
    
    def __init__(self):
        """Initialize message protocol."""
        self.message_handlers = {}
    
    def create_message(self,
                      message_type: MessageType,
                      data: Optional[Dict[str, Any]] = None,
                      reply_to: Optional[str] = None,
                      message_id: Optional[str] = None,
                      priority: MessagePriority = MessagePriority.MEDIUM) -> str:
        """
        Create a message according to the protocol.
        
        Args:
            message_type: Type of message
            data: Message payload data
            reply_to: ID of message this is replying to
            message_id: Unique message identifier (auto-generated if not provided)
            priority: Message priority level
            
        Returns:
            JSON-encoded message string
        """
        message = {
            "protocol_version": self.PROTOCOL_VERSION,
            "message_id": message_id or str(uuid.uuid4()),
            "type": message_type.value,
            "timestamp": datetime.utcnow().isoformat(),
            "priority": priority.value,
            "data": data or {}
        }
        
        if reply_to:
            message["reply_to"] = reply_to
        
        return json.dumps(message)
    
    def parse_message(self, raw_message: str) -> Dict[str, Any]:
        """
        Parse a raw message string.
        
        Args:
            raw_message: JSON-encoded message string
            
        Returns:
            Parsed message dictionary
            
        Raises:
            json.JSONDecodeError: If message is not valid JSON
            ValueError: If message structure is invalid
        """
        message = json.loads(raw_message)
        
        # Validate required fields
        required_fields = ["protocol_version", "message_id", "type", "timestamp"]
        for field in required_fields:
            if field not in message:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate protocol version
        if message["protocol_version"] != self.PROTOCOL_VERSION:
            raise ValueError(f"Unsupported protocol version: {message['protocol_version']}")
        
        # Validate message type
        try:
            message["message_type_enum"] = MessageType(message["type"])
        except ValueError:
            raise ValueError(f"Unknown message type: {message['type']}")
        
        return message
    
    def validate_message(self, message: Dict[str, Any]) -> bool:
        """
        Validate a parsed message.
        
        Args:
            message: Parsed message dictionary
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required fields
            if not all(field in message for field in ["protocol_version", "message_id", "type"]):
                return False
            
            # Check protocol version
            if message["protocol_version"] != self.PROTOCOL_VERSION:
                return False
            
            # Check message type
            if message["type"] not in [mt.value for mt in MessageType]:
                return False
            
            # Check timestamp format
            try:
                datetime.fromisoformat(message["timestamp"])
            except (ValueError, TypeError):
                return False
            
            return True
        
        except Exception:
            return False
    
    def create_error_message(self,
                           error: str,
                           error_code: Optional[str] = None,
                           details: Optional[Dict[str, Any]] = None,
                           reply_to: Optional[str] = None) -> str:
        """
        Create an error message.
        
        Args:
            error: Error message
            error_code: Optional error code
            details: Additional error details
            reply_to: ID of message this error is responding to
            
        Returns:
            JSON-encoded error message string
        """
        data = {
            "error": error,
            "error_code": error_code,
            "details": details or {}
        }
        
        return self.create_message(
            message_type=MessageType.ERROR,
            data=data,
            reply_to=reply_to,
            priority=MessagePriority.HIGH
        )
    
    def create_task_message(self,
                           task_id: str,
                           description: str,
                           parameters: Dict[str, Any],
                           priority: str = "medium",
                           agent_id: Optional[str] = None) -> str:
        """
        Create a task submission message.
        
        Args:
            task_id: Unique task identifier
            description: Task description
            parameters: Task parameters
            priority: Task priority
            agent_id: Optional specific agent ID
            
        Returns:
            JSON-encoded task message string
        """
        data = {
            "task_id": task_id,
            "description": description,
            "parameters": parameters,
            "priority": priority,
            "agent_id": agent_id
        }
        
        return self.create_message(
            message_type=MessageType.TASK_SUBMIT,
            data=data,
            priority=MessagePriority.MEDIUM
        )
    
    def create_agent_message(self,
                            from_agent: str,
                            to_agent: str,
                            message_content: Any,
                            message_type: str = "communication") -> str:
        """
        Create a message between agents.
        
        Args:
            from_agent: ID of sending agent
            to_agent: ID of receiving agent
            message_content: Message content
            message_type: Type of agent message
            
        Returns:
            JSON-encoded agent message string
        """
        data = {
            "from_agent": from_agent,
            "to_agent": to_agent,
            "message_type": message_type,
            "content": message_content,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self.create_message(
            message_type=MessageType.AGENT_MESSAGE,
            data=data,
            priority=MessagePriority.MEDIUM
        )
    
    def create_notification(self,
                           notification_type: str,
                           title: str,
                           message: str,
                           severity: str = "info") -> str:
        """
        Create a notification message.
        
        Args:
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            severity: Notification severity (info, warning, error, critical)
            
        Returns:
            JSON-encoded notification message string
        """
        data = {
            "type": notification_type,
            "title": title,
            "message": message,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self.create_message(
            message_type=MessageType.NOTIFICATION,
            data=data,
            priority=MessagePriority.MEDIUM
        )
    
    def create_event(self,
                    event_type: str,
                    event_data: Dict[str, Any],
                    source: Optional[str] = None) -> str:
        """
        Create an event message.
        
        Args:
            event_type: Type of event
            event_data: Event data
            source: Optional event source
            
        Returns:
            JSON-encoded event message string
        """
        data = {
            "event_type": event_type,
            "data": event_data,
            "source": source,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self.create_message(
            message_type=MessageType.EVENT,
            data=data,
            priority=MessagePriority.LOW
        )
    
    def get_message_type(self, raw_message: str) -> Optional[MessageType]:
        """
        Get the message type from a raw message without full parsing.
        
        Args:
            raw_message: Raw JSON message string
            
        Returns:
            MessageType enum or None if invalid
        """
        try:
            message = json.loads(raw_message)
            message_type_str = message.get("type")
            return MessageType(message_type_str) if message_type_str else None
        except (json.JSONDecodeError, ValueError):
            return None
    
    def is_error_message(self, raw_message: str) -> bool:
        """
        Check if a message is an error message.
        
        Args:
            raw_message: Raw JSON message string
            
        Returns:
            True if error message, False otherwise
        """
        return self.get_message_type(raw_message) == MessageType.ERROR
    
    def is_task_message(self, raw_message: str) -> bool:
        """
        Check if a message is task-related.
        
        Args:
            raw_message: Raw JSON message string
            
        Returns:
            True if task-related, False otherwise
        """
        msg_type = self.get_message_type(raw_message)
        task_types = [
            MessageType.TASK_SUBMIT,
            MessageType.TACK,
            MessageType.TASK_RESULT,
            MessageType.TASK_CANCEL,
            MessageType.TASK_STATUS
        ]
        return msg_type in task_types
    
    def extract_message_id(self, raw_message: str) -> Optional[str]:
        """
        Extract message ID from a raw message.
        
        Args:
            raw_message: Raw JSON message string
            
        Returns:
            Message ID string or None if not found
        """
        try:
            message = json.loads(raw_message)
            return message.get("message_id")
        except json.JSONDecodeError:
            return None


class MessageQueue:
    """
    Message queue for managing messages between components.
    Implements priority-based message handling.
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize message queue.
        
        Args:
            max_size: Maximum number of messages in queue
        """
        self.max_size = max_size
        self.queues = {
            priority: []
            for priority in MessagePriority
        }
        self.message_counts = {
            priority: 0
            for priority in MessagePriority
        }
    
    def enqueue(self, message: Dict[str, Any], priority: MessagePriority) -> bool:
        """
        Add a message to the queue.
        
        Args:
            message: Message dictionary
            priority: Message priority
            
        Returns:
            True if enqueued, False if queue is full
        """
        total_messages = sum(len(q) for q in self.queues.values())
        
        if total_messages >= self.max_size:
            return False
        
        self.queues[priority].append(message)
        self.message_counts[priority] += 1
        return True
    
    def dequeue(self) -> Optional[Dict[str, Any]]:
        """
        Get the next message from the queue (highest priority first).
        
        Returns:
            Message dictionary or None if queue is empty
        """
        # Check queues in priority order (CRITICAL to LOW)
        for priority in reversed(list(MessagePriority)):
            if self.queues[priority]:
                message = self.queues[priority].pop(0)
                self.message_counts[priority] -= 1
                return message
        
        return None
    
    def peek(self) -> Optional[Dict[str, Any]]:
        """
        Peek at the next message without removing it.
        
        Returns:
            Message dictionary or None if queue is empty
        """
        for priority in reversed(list(MessagePriority)):
            if self.queues[priority]:
                return self.queues[priority][0]
        
        return None
    
    def size(self) -> int:
        """Get total number of messages in queue."""
        return sum(len(q) for q in self.queues.values())
    
    def clear(self):
        """Clear all messages from the queue."""
        for priority in MessagePriority:
            self.queues[priority].clear()
            self.message_counts[priority] = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            "total_messages": self.size(),
            "max_size": self.max_size,
            "messages_by_priority": {
                priority.name: len(self.queues[priority])
                for priority in MessagePriority
            },
            "utilization": f"{(self.size() / self.max_size * 100):.1f}%"
        }