"""
OMNI-AI API Package
REST API, WebSocket, and communication interfaces
"""
from .rest_api import create_app
from .websocket_handler import WebSocketHandler
from .communication_protocol import MessageProtocol, MessageType

__all__ = [
    "create_app",
    "WebSocketHandler",
    "MessageProtocol",
    "MessageType"
]