"""
OMNI-AI WebSocket Handler
Provides real-time communication and streaming capabilities
"""
import asyncio
import json
from typing import Dict, Any, Optional, Set, TYPE_CHECKING
from datetime import datetime
import logging

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

if TYPE_CHECKING:
    from websockets.server import WebSocketServerProtocol

from ..nexus.orchestrator import NexusOrchestrator
from ..agents.base_agent import Task, AgentStatus
from .communication_protocol import MessageProtocol, MessageType


logger = logging.getLogger(__name__)


class WebSocketHandler:
    """
    WebSocket handler for real-time communication.
    Supports bidirectional messaging, streaming, and event notifications.
    """
    
    def __init__(self, orchestrator: NexusOrchestrator = None,
                 host: str = "0.0.0.0",
                 port: int = 8765):
        """
        Initialize WebSocket handler.
        
        Args:
            orchestrator: NEXUS orchestrator instance
            host: WebSocket server host
            port: WebSocket server port
        """
        self.orchestrator = orchestrator
        self.host = host
        self.port = port
        
        # Connected clients
        self.clients: Set[Any] = set()
        
        # Message protocol
        self.protocol = MessageProtocol()
        
        # Server instance
        self.server = None
        
        logger.info(f"WebSocketHandler initialized on {host}:{port}")
    
    async def handle_client(self, websocket: Any, path: str):
        """
        Handle a connected WebSocket client.
        
        Args:
            websocket: WebSocket connection
            path: WebSocket path
        """
        client_id = f"client_{id(websocket)}"
        logger.info(f"Client connected: {client_id}")
        
        # Add client to connected set
        self.clients.add(websocket)
        
        try:
            # Send welcome message
            welcome_msg = self.protocol.create_message(
                message_type=MessageType.WELCOME,
                data={
                    "client_id": client_id,
                    "server_time": datetime.utcnow().isoformat(),
                    "capabilities": ["task_submission", "streaming", "notifications"]
                }
            )
            await websocket.send(welcome_msg)
            
            # Handle incoming messages
            async for message in websocket:
                try:
                    await self.handle_message(websocket, client_id, message)
                except json.JSONDecodeError:
                    error_msg = self.protocol.create_message(
                        message_type=MessageType.ERROR,
                        data={"error": "Invalid JSON format"}
                    )
                    await websocket.send(error_msg)
                except Exception as e:
                    logger.error(f"Error handling message from {client_id}: {str(e)}")
                    error_msg = self.protocol.create_message(
                        message_type=MessageType.ERROR,
                        data={"error": str(e)}
                    )
                    await websocket.send(error_msg)
        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_id}")
        finally:
            # Remove client from connected set
            self.clients.discard(websocket)
            logger.info(f"Client removed: {client_id}")
    
    async def handle_message(self, websocket: Any,
                           client_id: str, raw_message: str):
        """
        Handle an incoming message from a client.
        
        Args:
            websocket: WebSocket connection
            client_id: Client identifier
            raw_message: Raw message string
        """
        # Parse message
        message = self.protocol.parse_message(raw_message)
        message_type = message.get("type")
        data = message.get("data", {})
        message_id = message.get("message_id")
        
        logger.debug(f"Received message from {client_id}: {message_type}")
        
        # Route message based on type
        if message_type == MessageType.TASK_SUBMIT.value:
            await self.handle_task_submit(websocket, client_id, message_id, data)
        
        elif message_type == MessageType.TASK_CANCEL.value:
            await self.handle_task_cancel(websocket, client_id, message_id, data)
        
        elif message_type == MessageType.TASK_STATUS.value:
            await self.handle_task_status(websocket, client_id, message_id, data)
        
        elif message_type == MessageType.AGENT_LIST.value:
            await self.handle_agent_list(websocket, client_id, message_id)
        
        elif message_type == MessageType.STREAM_START.value:
            await self.handle_stream_start(websocket, client_id, message_id, data)
        
        elif message_type == MessageType.STREAM_STOP.value:
            await self.handle_stream_stop(websocket, client_id, message_id, data)
        
        elif message_type == MessageType.SUBSCRIBE.value:
            await self.handle_subscribe(websocket, client_id, message_id, data)
        
        elif message_type == MessageType.UNSUBSCRIBE.value:
            await self.handle_unsubscribe(websocket, client_id, message_id, data)
        
        elif message_type == MessageType.PING.value:
            await self.handle_ping(websocket, client_id, message_id)
        
        else:
            error_msg = self.protocol.create_message(
                message_type=MessageType.ERROR,
                data={"error": f"Unknown message type: {message_type}"},
                reply_to=message_id
            )
            await websocket.send(error_msg)
    
    async def handle_task_submit(self, websocket: Any,
                                client_id: str, message_id: str, data: Dict[str, Any]):
        """
        Handle task submission request.
        
        Args:
            websocket: WebSocket connection
            client_id: Client identifier
            message_id: Message identifier
            data: Task data
        """
        if not self.orchestrator:
            error_msg = self.protocol.create_message(
                message_type=MessageType.ERROR,
                data={"error": "Orchestrator not available"},
                reply_to=message_id
            )
            await websocket.send(error_msg)
            return
        
        try:
            # Create task
            task = Task(
                task_id=data.get('task_id'),
                description=data['description'],
                parameters=data['parameters'],
                priority=data.get('priority', 'medium'),
                agent_id=data.get('agent_id'),
                clearance_level=data.get('clearance_level', 1)
            )
            
            # Submit task
            future = self.orchestrator.submit_task(task)
            
            # Send acknowledgment
            ack_msg = self.protocol.create_message(
                message_type=MessageType.TACK,
                data={
                    "task_id": task.task_id,
                    "status": "submitted",
                    "timestamp": datetime.utcnow().isoformat()
                },
                reply_to=message_id
            )
            await websocket.send(ack_msg)
            
            # Execute task and send result
            result = await future
            
            result_msg = self.protocol.create_message(
                message_type=MessageType.TASK_RESULT,
                data={
                    "task_id": result.task_id,
                    "agent_id": result.agent_id,
                    "status": result.status.value,
                    "result": result.result,
                    "timestamp": result.timestamp.isoformat()
                }
            )
            await websocket.send(result_msg)
        
        except Exception as e:
            error_msg = self.protocol.create_message(
                message_type=MessageType.ERROR,
                data={"error": str(e)},
                reply_to=message_id
            )
            await websocket.send(error_msg)
    
    async def handle_task_cancel(self, websocket: Any,
                                client_id: str, message_id: str, data: Dict[str, Any]):
        """
        Handle task cancellation request.
        
        Args:
            websocket: WebSocket connection
            client_id: Client identifier
            message_id: Message identifier
            data: Task cancellation data
        """
        task_id = data.get('task_id')
        
        if not task_id:
            error_msg = self.protocol.create_message(
                message_type=MessageType.ERROR,
                data={"error": "Missing task_id"},
                reply_to=message_id
            )
            await websocket.send(error_msg)
            return
        
        # Note: Task cancellation logic would be implemented in orchestrator
        # For now, send a response
        response_msg = self.protocol.create_message(
            message_type=MessageType.TASK_STATUS,
            data={
                "task_id": task_id,
                "status": "cancelled",
                "message": "Task cancellation requested"
            },
            reply_to=message_id
        )
        await websocket.send(response_msg)
    
    async def handle_task_status(self, websocket: Any,
                                client_id: str, message_id: str, data: Dict[str, Any]):
        """
        Handle task status request.
        
        Args:
            websocket: WebSocket connection
            client_id: Client identifier
            message_id: Message identifier
            data: Task status request data
        """
        task_id = data.get('task_id')
        
        if not task_id:
            error_msg = self.protocol.create_message(
                message_type=MessageType.ERROR,
                data={"error": "Missing task_id"},
                reply_to=message_id
            )
            await websocket.send(error_msg)
            return
        
        if not self.orchestrator:
            error_msg = self.protocol.create_message(
                message_type=MessageType.ERROR,
                data={"error": "Orchestrator not available"},
                reply_to=message_id
            )
            await websocket.send(error_msg)
            return
        
        # Get task from orchestrator
        task = self.orchestrator.task_queue.get(task_id)
        
        if task:
            status_msg = self.protocol.create_message(
                message_type=MessageType.TASK_STATUS,
                data={
                    "task_id": task.task_id,
                    "status": task.status.value,
                    "agent_id": task.agent_id,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None
                },
                reply_to=message_id
            )
            await websocket.send(status_msg)
        else:
            error_msg = self.protocol.create_message(
                message_type=MessageType.ERROR,
                data={"error": f"Task not found: {task_id}"},
                reply_to=message_id
            )
            await websocket.send(error_msg)
    
    async def handle_agent_list(self, websocket: Any,
                               client_id: str, message_id: str):
        """
        Handle agent list request.
        
        Args:
            websocket: WebSocket connection
            client_id: Client identifier
            message_id: Message identifier
        """
        if not self.orchestrator:
            error_msg = self.protocol.create_message(
                message_type=MessageType.ERROR,
                data={"error": "Orchestrator not available"},
                reply_to=message_id
            )
            await websocket.send(error_msg)
            return
        
        agents = []
        for agent in self.orchestrator.agents.values():
            agents.append({
                "agent_id": agent.agent_id,
                "name": agent.name,
                "description": agent.description,
                "capabilities": agent.capabilities,
                "status": agent.status.value
            })
        
        response_msg = self.protocol.create_message(
            message_type=MessageType.AGENT_LIST,
            data={
                "agents": agents,
                "count": len(agents)
            },
            reply_to=message_id
        )
        await websocket.send(response_msg)
    
    async def handle_stream_start(self, websocket: Any,
                                  client_id: str, message_id: str, data: Dict[str, Any]):
        """
        Handle stream start request.
        
        Args:
            websocket: WebSocket connection
            client_id: Client identifier
            message_id: Message identifier
            data: Stream configuration
        """
        stream_type = data.get('stream_type')
        
        # Send acknowledgment
        ack_msg = self.protocol.create_message(
            message_type=MessageType.STREAM_STARTED,
            data={
                "stream_type": stream_type,
                "status": "streaming",
                "message": f"Started {stream_type} stream"
            },
            reply_to=message_id
        )
        await websocket.send(ack_msg)
        
        # Start streaming (example implementation)
        if stream_type == "metrics":
            await self.stream_metrics(websocket)
        elif stream_type == "events":
            await self.stream_events(websocket)
        else:
            error_msg = self.protocol.create_message(
                message_type=MessageType.ERROR,
                data={"error": f"Unknown stream type: {stream_type}"},
                reply_to=message_id
            )
            await websocket.send(error_msg)
    
    async def handle_stream_stop(self, websocket: Any,
                                 client_id: str, message_id: str, data: Dict[str, Any]):
        """
        Handle stream stop request.
        
        Args:
            websocket: WebSocket connection
            client_id: Client identifier
            message_id: Message identifier
            data: Stream data
        """
        response_msg = self.protocol.create_message(
            message_type=MessageType.STREAM_STOPPED,
            data={
                "status": "stopped",
                "message": "Stream stopped"
            },
            reply_to=message_id
        )
        await websocket.send(response_msg)
    
    async def handle_subscribe(self, websocket: Any,
                              client_id: str, message_id: str, data: Dict[str, Any]):
        """
        Handle subscription request.
        
        Args:
            websocket: WebSocket connection
            client_id: Client identifier
            message_id: Message identifier
            data: Subscription data
        """
        event_type = data.get('event_type')
        
        # Store subscription (would be implemented with proper subscription manager)
        # For now, send acknowledgment
        ack_msg = self.protocol.create_message(
            message_type=MessageType.SUBSCRIPTION_CONFIRMED,
            data={
                "event_type": event_type,
                "status": "subscribed"
            },
            reply_to=message_id
        )
        await websocket.send(ack_msg)
    
    async def handle_unsubscribe(self, websocket: Any,
                                client_id: str, message_id: str, data: Dict[str, Any]):
        """
        Handle unsubscription request.
        
        Args:
            websocket: WebSocket connection
            client_id: Client identifier
            message_id: Message identifier
            data: Unsubscription data
        """
        event_type = data.get('event_type')
        
        ack_msg = self.protocol.create_message(
            message_type=MessageType.SUBSCRIPTION_CANCELLED,
            data={
                "event_type": event_type,
                "status": "unsubscribed"
            },
            reply_to=message_id
        )
        await websocket.send(ack_msg)
    
    async def handle_ping(self, websocket: Any,
                        client_id: str, message_id: str):
        """
        Handle ping message.
        
        Args:
            websocket: WebSocket connection
            client_id: Client identifier
            message_id: Message identifier
        """
        pong_msg = self.protocol.create_message(
            message_type=MessageType.PONG,
            data={
                "timestamp": datetime.utcnow().isoformat()
            },
            reply_to=message_id
        )
        await websocket.send(pong_msg)
    
    async def stream_metrics(self, websocket: Any):
        """
        Stream metrics to client.
        
        Args:
            websocket: WebSocket connection
        """
        while True:
            try:
                if not self.orchestrator:
                    break
                
                # Gather metrics from orchestrator and agents
                metrics = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "orchestrator": {
                        "active_tasks": len(self.orchestrator.task_queue)
                    },
                    "agents": {}
                }
                
                for agent_id, agent in self.orchestrator.agents.items():
                    metrics["agents"][agent_id] = {
                        "status": agent.status.value,
                        "tasks_completed": agent.metrics.tasks_completed,
                        "tasks_failed": agent.metrics.tasks_failed
                    }
                
                # Send metrics
                metrics_msg = self.protocol.create_message(
                    message_type=MessageType.STREAM_DATA,
                    data=metrics
                )
                await websocket.send(metrics_msg)
                
                # Wait before next update
                await asyncio.sleep(5)
            
            except Exception as e:
                logger.error(f"Error streaming metrics: {str(e)}")
                break
    
    async def stream_events(self, websocket: Any):
        """
        Stream events to client.
        
        Args:
            websocket: WebSocket connection
        """
        while True:
            try:
                # In a real implementation, this would stream actual events
                # For now, send periodic status updates
                event_msg = self.protocol.create_message(
                    message_type=MessageType.EVENT,
                    data={
                        "type": "system_status",
                        "message": "System operating normally",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                await websocket.send(event_msg)
                
                await asyncio.sleep(10)
            
            except Exception as e:
                logger.error(f"Error streaming events: {str(e)}")
                break
    
    async def broadcast_message(self, message_type: MessageType, data: Dict[str, Any]):
        """
        Broadcast a message to all connected clients.
        
        Args:
            message_type: Type of message to broadcast
            data: Message data
        """
        if not self.clients:
            return
        
        message = self.protocol.create_message(
            message_type=message_type,
            data=data
        )
        
        # Send to all connected clients
        disconnected = set()
        for client in self.clients:
            try:
                await client.send(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {str(e)}")
                disconnected.add(client)
        
        # Remove disconnected clients
        self.clients -= disconnected
    
    async def start(self):
        """Start the WebSocket server."""
        if not WEBSOCKETS_AVAILABLE:
            logger.error("websockets library not installed. Install with: pip install websockets")
            return
        
        logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        
        self.server = await websockets.serve(
            self.handle_client,
            self.host,
            self.port,
            ping_interval=30,
            ping_timeout=20
        )
        
        logger.info(f"WebSocket server started successfully")
    
    async def stop(self):
        """Stop the WebSocket server."""
        if self.server:
            logger.info("Stopping WebSocket server")
            self.server.close()
            await self.server.wait_closed()
            logger.info("WebSocket server stopped")