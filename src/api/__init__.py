"""
OMNI-AI API Package
REST API, WebSocket, and communication interfaces
"""

from .communication_protocol import MessageProtocol, MessageType
from .rest_api import create_app
from .websocket_handler import WebSocketHandler

__all__ = ["create_app", "WebSocketHandler", "MessageProtocol", "MessageType"]
