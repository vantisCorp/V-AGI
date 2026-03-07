"""
OMNI-AI REST API
Provides RESTful endpoints for interacting with the OMNI-AI system
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from typing import Dict, Any, List
import asyncio
from datetime import datetime
import os

from ..nexus.orchestrator import NexusOrchestrator
from ..agents.base_agent import Task, TaskPriority, AgentStatus
from ..security.aegis import AegisGuardian
from ..memory.working_memory import WorkingMemory
from ..memory.long_term_memory import LongTermMemory
from ..memory.vector_store import VectorStore


def create_app(orchestrator: NexusOrchestrator = None,
               aegis: AegisGuardian = None,
               working_memory: WorkingMemory = None,
               long_term_memory: LongTermMemory = None,
               vector_store: VectorStore = None) -> Flask:
    """
    Create and configure Flask application for OMNI-AI REST API.
    
    Args:
        orchestrator: NEXUS orchestrator instance
        aegis: AEGIS guardian instance
        working_memory: Working memory instance
        long_term_memory: Long-term memory instance
        vector_store: Vector store instance
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    CORS(app)
    
    # Store dependencies
    app.orchestrator = orchestrator
    app.aegis = aegis
    app.working_memory = working_memory
    app.long_term_memory = long_term_memory
    app.vector_store = vector_store
    
    # Configuration
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size
    
    @app.route('/')
    def index():
        """API root endpoint."""
        return jsonify({
            "name": "OMNI-AI REST API",
            "version": "1.0.0",
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "endpoints": {
                "health": "/health",
                "agents": "/api/agents",
                "tasks": "/api/tasks",
                "submit_task": "/api/tasks/submit",
                "memory": "/api/memory",
                "monitoring": "/api/monitoring"
            }
        })
    
    @app.route('/health')
    def health():
        """Health check endpoint."""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "orchestrator": "operational" if app.orchestrator else "not configured",
                "aegis": "operational" if app.aegis else "not configured",
                "working_memory": "operational" if app.working_memory else "not configured",
                "long_term_memory": "operational" if app.long_term_memory else "not configured",
                "vector_store": "operational" if app.vector_store else "not configured"
            }
        })
    
    @app.route('/api/agents', methods=['GET'])
    def list_agents():
        """List all registered agents."""
        if not app.orchestrator:
            return jsonify({"error": "Orchestrator not configured"}), 503
        
        agents = []
        for agent in app.orchestrator.agents.values():
            agents.append({
                "agent_id": agent.agent_id,
                "name": agent.name,
                "description": agent.description,
                "version": agent.version,
                "clearance_level": agent.clearance_level,
                "capabilities": agent.capabilities,
                "status": agent.status.value,
                "metrics": {
                    "tasks_received": agent.metrics.tasks_received,
                    "tasks_completed": agent.metrics.tasks_completed,
                    "tasks_failed": agent.metrics.tasks_failed
                }
            })
        
        return jsonify({
            "total_agents": len(agents),
            "agents": agents,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    @app.route('/api/agents/<agent_id>', methods=['GET'])
    def get_agent(agent_id: str):
        """Get details of a specific agent."""
        if not app.orchestrator:
            return jsonify({"error": "Orchestrator not configured"}), 503
        
        agent = app.orchestrator.agents.get(agent_id)
        if not agent:
            return jsonify({"error": f"Agent not found: {agent_id}"}), 404
        
        return jsonify({
            "agent_id": agent.agent_id,
            "name": agent.name,
            "description": agent.description,
            "version": agent.version,
            "clearance_level": agent.clearance_level,
            "capabilities": agent.capabilities,
            "status": agent.status.value,
            "metrics": {
                "tasks_received": agent.metrics.tasks_received,
                "tasks_completed": agent.metrics.tasks_completed,
                "tasks_failed": agent.metrics.tasks_failed,
                "success_rate": agent.metrics.success_rate()
            },
            "task_history": list(agent.task_history.keys())[-10:]  # Last 10 tasks
        })
    
    @app.route('/api/tasks', methods=['GET'])
    def list_tasks():
        """List all tasks."""
        if not app.orchestrator:
            return jsonify({"error": "Orchestrator not configured"}), 503
        
        limit = request.args.get('limit', 50, type=int)
        status = request.args.get('status', None)
        
        tasks = list(app.orchestrator.task_queue.values())
        
        # Filter by status if specified
        if status:
            tasks = [t for t in tasks if t.status.value == status]
        
        # Limit results
        tasks = tasks[-limit:]
        
        return jsonify({
            "total_tasks": len(tasks),
            "tasks": [
                {
                    "task_id": t.task_id,
                    "description": t.description,
                    "status": t.status.value,
                    "priority": t.priority.value,
                    "agent_id": t.agent_id,
                    "created_at": t.created_at.isoformat() if t.created_at else None
                }
                for t in tasks
            ],
            "timestamp": datetime.utcnow().isoformat()
        })
    
    @app.route('/api/tasks/<task_id>', methods=['GET'])
    def get_task(task_id: str):
        """Get details of a specific task."""
        if not app.orchestrator:
            return jsonify({"error": "Orchestrator not configured"}), 503
        
        task = app.orchestrator.task_queue.get(task_id)
        if not task:
            return jsonify({"error": f"Task not found: {task_id}"}), 404
        
        return jsonify({
            "task_id": task.task_id,
            "description": task.description,
            "parameters": task.parameters,
            "status": task.status.value,
            "priority": task.priority.value,
            "agent_id": task.agent_id,
            "clearance_level": task.clearance_level,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            "result": task.result if task.result else None
        })
    
    @app.route('/api/tasks/submit', methods=['POST'])
    def submit_task():
        """Submit a new task for execution."""
        if not app.orchestrator:
            return jsonify({"error": "Orchestrator not configured"}), 503
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['description', 'parameters']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Apply AEGIS security filtering if available
        if app.aegis:
            filtered_data = app.aegis.filter_input(data)
            if filtered_data.get("blocked"):
                return jsonify({
                    "error": "Input blocked by AEGIS security layer",
                    "reason": filtered_data.get("reason")
                }), 403
        
        # Create task
        try:
            task = Task(
                task_id=data.get('task_id'),
                description=data['description'],
                parameters=data['parameters'],
                priority=TaskPriority(data.get('priority', 'medium').lower()),
                agent_id=data.get('agent_id'),
                clearance_level=data.get('clearance_level', 1)
            )
        except ValueError as e:
            return jsonify({"error": f"Invalid task data: {str(e)}"}), 400
        
        # Submit task to orchestrator
        try:
            future = app.orchestrator.submit_task(task)
            result = asyncio.run(future)
            
            return jsonify({
                "task_id": result.task_id,
                "agent_id": result.agent_id,
                "status": result.status.value,
                "result": result.result,
                "timestamp": result.timestamp.isoformat()
            })
        except Exception as e:
            return jsonify({"error": f"Task execution failed: {str(e)}"}), 500
    
    @app.route('/api/tasks/submit/batch', methods=['POST'])
    def submit_tasks_batch():
        """Submit multiple tasks for batch execution."""
        if not app.orchestrator:
            return jsonify({"error": "Orchestrator not configured"}), 503
        
        data = request.get_json()
        
        if 'tasks' not in data:
            return jsonify({"error": "Missing required field: tasks"}), 400
        
        tasks = []
        results = []
        
        # Create tasks
        for task_data in data['tasks']:
            try:
                task = Task(
                    task_id=task_data.get('task_id'),
                    description=task_data['description'],
                    parameters=task_data['parameters'],
                    priority=TaskPriority(task_data.get('priority', 'medium').lower()),
                    agent_id=task_data.get('agent_id'),
                    clearance_level=task_data.get('clearance_level', 1)
                )
                tasks.append(task)
            except ValueError as e:
                results.append({
                    "error": f"Invalid task data: {str(e)}"
                })
        
        # Execute tasks
        for task in tasks:
            try:
                future = app.orchestrator.submit_task(task)
                result = asyncio.run(future)
                results.append({
                    "task_id": result.task_id,
                    "status": result.status.value,
                    "result": result.result
                })
            except Exception as e:
                results.append({
                    "task_id": task.task_id,
                    "error": str(e)
                })
        
        return jsonify({
            "total_tasks": len(tasks),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    @app.route('/api/memory/working', methods=['GET', 'POST', 'DELETE'])
    def working_memory_operations():
        """Working memory operations."""
        if not app.working_memory:
            return jsonify({"error": "Working memory not configured"}), 503
        
        if request.method == 'GET':
            key = request.args.get('key')
            if key:
                value = app.working_memory.get(key)
                return jsonify({"key": key, "value": value})
            else:
                # Get all keys
                return jsonify({
                    "keys": list(app.working_memory.cache.keys()),
                    "size": len(app.working_memory.cache)
                })
        
        elif request.method == 'POST':
            data = request.get_json()
            key = data.get('key')
            value = data.get('value')
            ttl = data.get('ttl', 3600)
            
            if not key or value is None:
                return jsonify({"error": "Missing required fields: key, value"}), 400
            
            app.working_memory.set(key, value, ttl)
            return jsonify({
                "status": "stored",
                "key": key,
                "ttl": ttl
            })
        
        elif request.method == 'DELETE':
            key = request.args.get('key')
            if not key:
                return jsonify({"error": "Missing required parameter: key"}), 400
            
            deleted = app.working_memory.delete(key)
            return jsonify({
                "status": "deleted" if deleted else "not_found",
                "key": key
            })
    
    @app.route('/api/memory/long-term/nodes', methods=['POST'])
    def store_knowledge_node():
        """Store a knowledge node in long-term memory."""
        if not app.long_term_memory:
            return jsonify({"error": "Long-term memory not configured"}), 503
        
        data = request.get_json()
        
        required_fields = ['node_id', 'node_type', 'properties']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        try:
            asyncio.run(app.long_term_memory.store_node(
                node_id=data['node_id'],
                node_type=data['node_type'],
                properties=data['properties']
            ))
            return jsonify({"status": "stored", "node_id": data['node_id']})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/memory/long-term/nodes/<node_id>', methods=['GET'])
    def get_knowledge_node(node_id: str):
        """Get a knowledge node from long-term memory."""
        if not app.long_term_memory:
            return jsonify({"error": "Long-term memory not configured"}), 503
        
        try:
            node = asyncio.run(app.long_term_memory.get_node(node_id))
            if node:
                return jsonify({"node": node})
            else:
                return jsonify({"error": "Node not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/memory/long-term/search', methods=['POST'])
    def search_knowledge_graph():
        """Search the knowledge graph."""
        if not app.long_term_memory:
            return jsonify({"error": "Long-term memory not configured"}), 503
        
        data = request.get_json()
        query = data.get('query', '')
        node_type = data.get('node_type')
        
        try:
            results = asyncio.run(app.long_term_memory.search_nodes(
                query=query,
                node_type=node_type
            ))
            return jsonify({
                "query": query,
                "results": results,
                "count": len(results)
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/memory/vector/search', methods=['POST'])
    def search_vector_store():
        """Search vector store for similar documents."""
        if not app.vector_store:
            return jsonify({"error": "Vector store not configured"}), 503
        
        data = request.get_json()
        query = data.get('query', '')
        top_k = data.get('top_k', 5)
        
        try:
            results = asyncio.run(app.vector_store.search(
                query=query,
                top_k=top_k
            ))
            return jsonify({
                "query": query,
                "results": results,
                "count": len(results)
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/memory/vector/store', methods=['POST'])
    def store_vector_document():
        """Store a document in vector store."""
        if not app.vector_store:
            return jsonify({"error": "Vector store not configured"}), 503
        
        data = request.get_json()
        
        required_fields = ['text', 'metadata']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        try:
            asyncio.run(app.vector_store.add_document(
                text=data['text'],
                metadata=data['metadata']
            ))
            return jsonify({"status": "stored"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/monitoring/metrics', methods=['GET'])
    def get_metrics():
        """Get system metrics."""
        if not app.orchestrator:
            return jsonify({"error": "Orchestrator not configured"}), 503
        
        metrics = {
            "orchestrator": {
                "active_tasks": len([t for t in app.orchestrator.task_queue.values() if t.status.value == "working"]),
                "pending_tasks": len([t for t in app.orchestrator.task_queue.values() if t.status.value == "idle"]),
                "completed_tasks": len([t for t in app.orchestrator.task_queue.values() if t.status.value == "completed"]),
                "failed_tasks": len([t for t in app.orchestrator.task_queue.values() if t.status.value == "failed"])
            },
            "agents": {}
        }
        
        for agent_id, agent in app.orchestrator.agents.items():
            metrics["agents"][agent_id] = {
                "status": agent.status.value,
                "tasks_received": agent.metrics.tasks_received,
                "tasks_completed": agent.metrics.tasks_completed,
                "tasks_failed": agent.metrics.tasks_failed,
                "success_rate": agent.metrics.success_rate()
            }
        
        return jsonify(metrics)
    
    @app.route('/api/monitoring/health', methods=['GET'])
    def get_system_health():
        """Get system health status."""
        health = {
            "overall_status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {}
        }
        
        # Check orchestrator
        if app.orchestrator:
            orchestrator_status = "operational"
            # Check if all agents are responsive
            non_responsive = sum(1 for a in app.orchestrator.agents.values() if a.status.value == "failed")
            if non_responsive > 0:
                orchestrator_status = "degraded"
            health["components"]["orchestrator"] = {
                "status": orchestrator_status,
                "active_agents": len(app.orchestrator.agents),
                "non_responsive_agents": non_responsive
            }
        else:
            health["components"]["orchestrator"] = {"status": "not_configured"}
            health["overall_status"] = "degraded"
        
        # Check memory systems
        memory_systems = [
            ("working_memory", app.working_memory),
            ("long_term_memory", app.long_term_memory),
            ("vector_store", app.vector_store)
        ]
        
        for name, system in memory_systems:
            if system:
                health["components"][name] = {"status": "operational"}
            else:
                health["components"][name] = {"status": "not_configured"}
                if health["overall_status"] == "healthy":
                    health["overall_status"] = "degraded"
        
        return jsonify(health)
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500
    
    return app