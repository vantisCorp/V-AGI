# OMNI-AI API Integration Summary

## Overview

OMNI-AI provides comprehensive API integration capabilities for external communication, including REST endpoints, WebSocket connections, and message queue integration. This document summarizes the implemented API components and their usage.

---

## Implemented Components

### 1. REST API (`src/api/rest_api.py`)

A Flask-based RESTful API providing HTTP endpoints for interacting with OMNI-AI.

#### Key Features
- **CORS Enabled**: Cross-Origin Resource Sharing for web applications
- **AEGIS Integration**: Automatic security filtering for all inputs
- **Async Task Execution**: Non-blocking task submission and execution
- **Memory System Access**: Direct access to working, long-term, and vector memory
- **Monitoring Endpoints**: System health and metrics

#### Available Endpoints

##### System Endpoints
```
GET  /                          - API information and endpoints
GET  /health                    - Health check status
```

##### Agent Management
```
GET  /api/agents                 - List all registered agents
GET  /api/agents/<agent_id>     - Get details of a specific agent
```

##### Task Management
```
GET  /api/tasks                  - List all tasks
GET  /api/tasks/<task_id>      - Get details of a specific task
POST /api/tasks/submit           - Submit a new task
POST /api/tasks/submit/batch     - Submit multiple tasks for batch execution
```

##### Memory Operations
```
GET    /api/memory/working        - Get working memory data
POST   /api/memory/working        - Store data in working memory
DELETE /api/memory/working        - Delete data from working memory
POST   /api/memory/long-term/nodes                    - Store knowledge node
GET    /api/memory/long-term/nodes/<node_id>          - Get knowledge node
POST   /api/memory/long-term/search                   - Search knowledge graph
POST   /api/memory/vector/search                      - Search vector store
POST   /api/memory/vector/store                       - Store in vector store
```

##### Monitoring
```
GET /api/monitoring/metrics       - Get system metrics
GET /api/monitoring/health        - Get system health status
```

#### Example Usage

##### Submit a Task
```bash
curl -X POST http://localhost:5000/api/tasks/submit \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Verify facts about climate change",
    "parameters": {
      "task_type": "fact_verification",
      "claims": ["Global temperatures have risen by 1.1°C"]
    },
    "priority": "medium"
  }'
```

##### List Agents
```bash
curl http://localhost:5000/api/agents
```

##### Store in Working Memory
```bash
curl -X POST http://localhost:5000/api/memory/working \
  -H "Content-Type: application/json" \
  -d '{
    "key": "user_session",
    "value": {"user_id": "123", "timestamp": "2025-01-18"},
    "ttl": 3600
  }'
```

---

### 2. WebSocket Handler (`src/api/websocket_handler.py`)

Real-time bidirectional communication supporting streaming and live updates.

#### Key Features
- **Bidirectional Messaging**: Full-duplex communication
- **Real-time Streaming**: Live metrics and event streaming
- **Connection Management**: Client connection tracking
- **Message Protocol**: Structured message format
- **Event Subscription**: Subscribe to specific event types

#### Supported Message Types

##### Connection Management
- `welcome` - Welcome message sent on connection
- `ping` / `pong` - Connection health check
- `goodbye` - Connection closure

##### Task Management
- `task_submit` - Submit a task
- `task_ack` - Task acknowledgment
- `task_result` - Task completion result
- `task_cancel` - Cancel a task
- `task_status` - Query task status

##### Agent Management
- `agent_list` - List available agents
- `agent_status` - Get agent status

##### Streaming
- `stream_start` - Start a stream
- `stream_started` - Stream started confirmation
- `stream_data` - Stream data
- `stream_stop` - Stop a stream
- `stream_stopped` - Stream stopped confirmation

##### Subscriptions
- `subscribe` - Subscribe to events
- `subscription_confirmed` - Subscription confirmation
- `unsubscribe` - Unsubscribe from events
- `subscription_cancelled` - Unsubscription confirmation

##### Events & Notifications
- `event` - System events
- `notification` - Notifications
- `error` - Error messages

#### Example Usage

##### Connect and Submit Task
```javascript
const ws = new WebSocket('ws://localhost:8765');

ws.onopen = () => {
    // Submit a task
    const message = {
        protocol_version: "1.0.0",
        message_id: "msg-001",
        type: "task_submit",
        timestamp: new Date().toISOString(),
        priority: 1,
        data: {
            task_id: "task-001",
            description: "Verify facts",
            parameters: {
                task_type: "fact_verification",
                claims: ["Test claim"]
            }
        }
    };
    ws.send(JSON.stringify(message));
};

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    console.log('Received:', message);
};
```

##### Start Metrics Stream
```javascript
ws.send(JSON.stringify({
    protocol_version: "1.0.0",
    message_id: "msg-002",
    type: "stream_start",
    timestamp: new Date().toISOString(),
    data: {
        stream_type: "metrics"
    }
}));
```

---

### 3. Communication Protocol (`src/api/communication_protocol.py`)

Standardized message format and protocol for all OMNI-AI communications.

#### Message Structure
```json
{
    "protocol_version": "1.0.0",
    "message_id": "unique-identifier",
    "type": "message_type",
    "timestamp": "2025-01-18T10:30:00Z",
    "priority": 1,
    "reply_to": "optional-message-id",
    "data": {
        // Message-specific data
    }
}
```

#### Message Priorities
- `LOW (0)` - Low priority messages
- `MEDIUM (1)` - Normal priority (default)
- `HIGH (2)` - Important messages
- `CRITICAL (3)` - Urgent messages

#### Protocol Features
- **Version Control**: Protocol version for compatibility
- **Message IDs**: Unique identifiers for tracking
- **Timestamps**: Accurate timing information
- **Priority Levels**: Priority-based message handling
- **Reply Chains**: Support for message threading
- **Validation**: Message structure validation

#### Message Queue
Built-in priority-based message queue implementation:
- Separate queues for each priority level
- Automatic prioritization
- Queue statistics and monitoring
- Thread-safe operations

#### Example Usage

```python
from src.api.communication_protocol import MessageProtocol, MessageType

protocol = MessageProtocol()

# Create a task message
task_message = protocol.create_task_message(
    task_id="task-001",
    description="Verify facts",
    parameters={"claims": ["Test claim"]},
    priority="medium"
)

# Create an error message
error_message = protocol.create_error_message(
    error="Task execution failed",
    error_code="EXEC_ERROR",
    details={"task_id": "task-001"}
)

# Create a notification
notification = protocol.create_notification(
    notification_type="task_completed",
    title="Task Complete",
    message="Task task-001 has completed successfully",
    severity="info"
)
```

---

### 4. Message Queue Integration (`src/api/message_queue_integration.py`)

Integration with external message queue systems for distributed messaging.

#### Supported Providers
- **Redis**: Pub/Sub messaging
- **RabbitMQ**: AMQP messaging
- **Kafka**: High-throughput streaming (planned)
- **AWS SQS**: Cloud-based queue (planned)

#### Key Features
- **Async Operations**: Fully asynchronous implementation
- **Multiple Providers**: Support for different queue systems
- **Topic-based Messaging**: Publish/Subscribe pattern
- **Message Handlers**: Register handlers for specific message types
- **Connection Management**: Automatic connection handling

#### Example Usage

##### Redis Integration
```python
from src.api.message_queue_integration import (
    MessageQueueIntegration, QueueProvider
)

# Create Redis integration
mq = MessageQueueIntegration(
    provider=QueueProvider.REDIS,
    host="localhost",
    port=6379,
    password="your-password"
)

# Connect
await mq.connect()

# Publish a message
await mq.publish(
    topic="tasks",
    message={
        "type": "task_submit",
        "data": {
            "task_id": "task-001",
            "description": "Verify facts"
        }
    }
)

# Subscribe to a topic
async def handle_message(message):
    print(f"Received: {message}")

await mq.subscribe("tasks", handle_message)

# Disconnect
await mq.disconnect()
```

##### RabbitMQ Integration
```python
# Create RabbitMQ integration
mq = MessageQueueIntegration(
    provider=QueueProvider.RABBITMQ,
    host="localhost",
    port=5672,
    username="guest",
    password="guest"
)

# Connect and use (same API as Redis)
await mq.connect()
await mq.publish("tasks", message)
await mq.subscribe("tasks", handler)
```

##### Send Task via Queue
```python
await mq.send_task(
    task_queue="omni_tasks",
    task_id="task-001",
    description="Verify facts about climate change",
    parameters={
        "task_type": "fact_verification",
        "claims": ["Global temperatures have risen"]
    },
    priority="high"
)
```

##### Broadcast Event
```python
await mq.broadcast_event(
    event_type="system_alert",
    event_data={
        "severity": "warning",
        "message": "High CPU usage detected"
    },
    source="monitoring"
)
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    OMNI-AI System                        │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   REST API   │  │  WebSocket   │  │  Message     │ │
│  │   (Flask)    │  │   Handler    │  │   Queue      │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         │                 │                 │           │
│         └─────────────────┼─────────────────┘           │
│                           │                             │
│              ┌────────────▼────────────┐                │
│              │  Communication Protocol│                │
│              │    (Message Format)     │                │
│              └────────────┬────────────┘                │
│                           │                             │
│         ┌─────────────────┼─────────────────┐           │
│         │                 │                 │           │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐   │
│  │    AEGIS    │  │   NEXUS     │  │   Memory    │   │
│  │  (Security) │  │ (Orchestrator)│  │   Systems   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘   │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## Configuration

### Environment Variables

```bash
# REST API
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False

# WebSocket
WS_HOST=0.0.0.0
WS_PORT=8765

# Redis (for message queue)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# RabbitMQ (for message queue)
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
```

### Starting the Services

#### REST API
```bash
python -m src.api.rest_api
```

#### WebSocket Server
```python
from src.api.websocket_handler import WebSocketHandler

ws_handler = WebSocketHandler(host="0.0.0.0", port=8765)
await ws_handler.start()
```

#### Using Message Queue
```python
from src.api.message_queue_integration import MessageQueueIntegration

mq = MessageQueueIntegration(
    provider=QueueProvider.REDIS,
    host="localhost",
    port=6379
)
await mq.connect()
```

---

## Security Features

### AEGIS Integration
All API endpoints are protected by AEGIS security layer:
- Input filtering and validation
- Malicious pattern detection
- Sensitive information redaction
- Policy violation checking

### Authentication & Authorization
- Clearance level enforcement (1-3)
- Agent access control
- Task permission checking

### Rate Limiting
- Configurable rate limits per endpoint
- Protection against abuse
- Automatic throttling

---

## Performance Considerations

### REST API
- **Async Task Execution**: Non-blocking task submission
- **Connection Pooling**: Efficient database connections
- **Caching**: Response caching for frequently accessed data

### WebSocket
- **Binary Messages**: Efficient data transmission
- **Ping/Pong**: Connection health monitoring
- **Automatic Reconnection**: Client-side reconnection logic

### Message Queue
- **Priority Queues**: High-priority messages processed first
- **Batch Operations**: Efficient bulk message handling
- **Connection Reuse**: Persistent connections

---

## Error Handling

### Error Response Format
```json
{
    "error": "Error message",
    "error_code": "ERROR_CODE",
    "details": {
        "additional": "information"
    }
}
```

### HTTP Status Codes
- `200 OK` - Successful request
- `400 Bad Request` - Invalid request data
- `403 Forbidden` - AEGIS blocked the request
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service not configured

---

## Monitoring & Logging

### Metrics Available
- Request counts per endpoint
- Response times
- Error rates
- Active connections
- Queue sizes

### Logging
- Structured logging with timestamps
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Request/Response logging
- Error stack traces

---

## Best Practices

### REST API
1. Always check response status codes
2. Handle errors gracefully
3. Use appropriate HTTP methods
4. Validate input data before submission
5. Implement retry logic for failed requests

### WebSocket
1. Handle connection failures
2. Implement reconnection logic
3. Use message acknowledgments
4. Subscribe only to needed events
5. Close connections when done

### Message Queue
1. Use appropriate priority levels
2. Handle message processing errors
3. Implement dead-letter queues
4. Monitor queue sizes
5. Use connection pooling

---

## Future Enhancements

### Planned Features
- GraphQL API
- gRPC services
- WebSocket authentication
- Message queue clustering
- Load balancing
- API versioning
- Rate limiting per user
- Request throttling
- API documentation (Swagger/OpenAPI)

### Performance Optimizations
- Response compression
- Request batching
- Connection keep-alive
- Caching strategies
- Database query optimization

---

## Troubleshooting

### Common Issues

**REST API not starting**
- Check if Flask is installed: `pip install flask flask-cors`
- Verify port is not in use
- Check environment variables

**WebSocket connection failing**
- Verify websockets library is installed
- Check firewall settings
- Ensure correct host and port

**Message queue connection errors**
- Verify Redis/RabbitMQ is running
- Check credentials and connection parameters
- Test connectivity with Redis CLI or RabbitMQ admin

### Getting Help
- Check logs: `logs/omni_ai.log`
- Review API documentation
- Test endpoints with curl or Postman
- Enable debug mode for detailed error messages

---

## Conclusion

The OMNI-AI API integration provides a comprehensive set of tools for external communication, supporting REST, WebSocket, and message queue interfaces. These components enable flexible integration with various applications and services while maintaining security, performance, and reliability.

For more information, see:
- QUICK_START_GUIDE.md - Usage examples
- SPECIALIZED_AGENTS_SUMMARY.md - Agent capabilities
- IMPLEMENTATION_STATUS.md - Project status