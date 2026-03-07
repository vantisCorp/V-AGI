"""
NEXUS Orchestrator for OMNI-AI

Central orchestration system that coordinates multi-agent operations,
task decomposition, and resource management.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import uuid
from enum import Enum
from loguru import logger

from agents.base_agent import BaseAgent, Task, AgentResponse, TaskPriority
from agents import AgentCapabilities
from security import SecurityLevel
from memory.working_memory import WorkingMemory
from memory.long_term_memory import LongTermMemory


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class OrchestratedTask:
    """Task managed by NEXUS orchestrator."""
    task: Task
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[str] = None
    subtasks: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class AgentAssignment:
    """Agent assignment record."""
    agent_id: str
    task_id: str
    assigned_at: datetime = field(default_factory=datetime.utcnow)
    priority: TaskPriority = TaskPriority.MEDIUM


class NexusOrchestrator:
    """
    NEXUS Orchestrator - Central multi-agent coordination system.
    
    Features:
    - Task decomposition and distribution
    - Agent selection and assignment
    - Dependency management
    - Resource optimization
    - Progress tracking
    - Error handling and recovery
    """
    
    def __init__(
        self,
        max_concurrent_agents: int = 10,
        working_memory: Optional[WorkingMemory] = None,
        long_term_memory: Optional[LongTermMemory] = None
    ):
        """
        Initialize NEXUS orchestrator.
        
        Args:
            max_concurrent_agents: Maximum number of concurrent agent operations
            working_memory: Working memory instance
            long_term_memory: Long-term memory instance
        """
        self.max_concurrent_agents = max_concurrent_agents
        self.working_memory = working_memory or WorkingMemory()
        self.long_term_memory = long_term_memory
        
        # Agent registry
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_capabilities: Dict[str, AgentCapabilities] = {}
        
        # Task management
        self.tasks: Dict[str, OrchestratedTask] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.active_assignments: List[AgentAssignment] = []
        
        # Runtime state
        self.is_running = False
        self.worker_tasks: List[asyncio.Task] = []
        self._lock = asyncio.Lock()
        
        logger.info("NEXUS Orchestrator initialized")
    
    async def register_agent(
        self,
        agent: BaseAgent,
        capabilities: AgentCapabilities
    ) -> None:
        """
        Register an agent with the orchestrator.
        
        Args:
            agent: Agent instance to register
            capabilities: Agent capabilities
        """
        await agent.initialize()
        self.agents[agent.agent_id] = agent
        self.agent_capabilities[agent.agent_id] = capabilities
        
        logger.info(f"Registered agent: {agent.agent_id} with capabilities: {capabilities.name}")
    
    async def unregister_agent(self, agent_id: str) -> None:
        """
        Unregister an agent from the orchestrator.
        
        Args:
            agent_id: ID of agent to unregister
        """
        if agent_id in self.agents:
            await self.agents[agent_id].shutdown()
            del self.agents[agent_id]
            del self.agent_capabilities[agent_id]
            logger.info(f"Unregistered agent: {agent_id}")
    
    async def submit_task(
        self,
        description: str,
        parameters: Dict[str, Any] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        deadline: Optional[datetime] = None
    ) -> str:
        """
        Submit a task for execution.
        
        Args:
            description: Task description
            parameters: Task parameters
            priority: Task priority
            deadline: Task deadline
            
        Returns:
            Task ID
        """
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        task = Task(
            id=task_id,
            description=description,
            parameters=parameters or {},
            priority=priority,
            deadline=deadline
        )
        
        orchestrated_task = OrchestratedTask(task=task)
        
        async with self._lock:
            self.tasks[task_id] = orchestrated_task
        
        await self.task_queue.put(task_id)
        
        logger.info(f"Task submitted: {task_id} - {description}")
        
        return task_id
    
    async def start(self) -> None:
        """Start the orchestrator and worker tasks."""
        if self.is_running:
            logger.warning("Orchestrator is already running")
            return
        
        self.is_running = True
        
        # Start worker tasks
        for i in range(self.max_concurrent_agents):
            worker_task = asyncio.create_task(self._worker(f"worker_{i}"))
            self.worker_tasks.append(worker_task)
        
        logger.info(f"NEXUS Orchestrator started with {len(self.worker_tasks)} workers")
    
    async def stop(self) -> None:
        """Stop the orchestrator and cleanup resources."""
        self.is_running = False
        
        # Cancel worker tasks
        for worker_task in self.worker_tasks:
            worker_task.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        self.worker_tasks.clear()
        
        # Shutdown all agents
        for agent in self.agents.values():
            await agent.shutdown()
        
        logger.info("NEXUS Orchestrator stopped")
    
    async def _worker(self, worker_id: str) -> None:
        """
        Worker task that processes tasks from the queue.
        
        Args:
            worker_id: Worker identifier
        """
        logger.debug(f"Worker {worker_id} started")
        
        while self.is_running:
            try:
                # Get task from queue with timeout
                task_id = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )
                
                await self._process_task(task_id, worker_id)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
    
    async def _process_task(self, task_id: str, worker_id: str) -> None:
        """
        Process a single task.
        
        Args:
            task_id: Task ID to process
            worker_id: Worker identifier
        """
        async with self._lock:
            orchestrated_task = self.tasks.get(task_id)
            if not orchestrated_task:
                logger.error(f"Task not found: {task_id}")
                return
            
            orchestrated_task.status = TaskStatus.ASSIGNED
        
        # Decompose task if necessary
        subtasks = await self._decompose_task(orchestrated_task.task)
        
        if subtasks:
            # Execute subtasks
            results = []
            for subtask in subtasks:
                result = await self._execute_subtask(subtask, worker_id)
                results.append(result)
            
            # Aggregate results
            final_result = await self._aggregate_results(results)
        else:
            # Execute directly
            final_result = await self._execute_task_direct(orchestrated_task.task, worker_id)
        
        # Update task status
        async with self._lock:
            orchestrated_task.status = TaskStatus.COMPLETED
            orchestrated_task.completed_at = datetime.utcnow()
            orchestrated_task.result = final_result
        
        logger.info(f"Task {task_id} completed by worker {worker_id}")
    
    async def _decompose_task(self, task: Task) -> List[Task]:
        """
        Decompose a complex task into subtasks.
        
        Args:
            task: Task to decompose
            
        Returns:
            List of subtasks
        """
        # Simple decomposition logic - can be enhanced with ML-based decomposition
        if task.priority == TaskPriority.CRITICAL:
            # Decompose critical tasks into smaller subtasks
            subtasks = []
            for i in range(3):
                subtask = Task(
                    id=f"{task.id}_sub{i}",
                    description=f"Subtask {i+1}: {task.description}",
                    parameters=task.parameters,
                    priority=TaskPriority.HIGH,
                    deadline=task.deadline
                )
                subtasks.append(subtask)
            return subtasks
        
        return []
    
    async def _execute_subtask(self, task: Task, worker_id: str) -> AgentResponse:
        """
        Execute a subtask.
        
        Args:
            task: Subtask to execute
            worker_id: Worker identifier
            
        Returns:
            Agent response
        """
        # Select appropriate agent
        agent = await self._select_agent(task)
        
        if not agent:
            return AgentResponse(
                task_id=task.id,
                agent_id="none",
                status="error",
                error="No suitable agent found"
            )
        
        # Execute task
        response = await agent.execute_task(task)
        
        # Record response
        agent.record_response(response)
        
        return response
    
    async def _execute_task_direct(self, task: Task, worker_id: str) -> AgentResponse:
        """
        Execute a task directly without decomposition.
        
        Args:
            task: Task to execute
            worker_id: Worker identifier
            
        Returns:
            Agent response
        """
        # Select appropriate agent
        agent = await self._select_agent(task)
        
        if not agent:
            return AgentResponse(
                task_id=task.id,
                agent_id="none",
                status="error",
                error="No suitable agent found"
            )
        
        # Execute task
        response = await agent.execute_task(task)
        
        # Record response
        agent.record_response(response)
        
        return response
    
    async def _select_agent(self, task: Task) -> Optional[BaseAgent]:
        """
        Select the best agent for a task.
        
        Args:
            task: Task to assign
            
        Returns:
            Selected agent or None
        """
        # Simple selection logic - can be enhanced with ML-based selection
        available_agents = []
        
        for agent_id, agent in self.agents.items():
            status = await agent.get_status()
            task_count = await agent.get_task_count()
            
            if status.value == "idle" or task_count < agent.capabilities.max_concurrent_tasks:
                available_agents.append((agent, task_count))
        
        if not available_agents:
            return None
        
        # Select agent with least tasks
        available_agents.sort(key=lambda x: x[1])
        return available_agents[0][0]
    
    async def _aggregate_results(self, results: List[AgentResponse]) -> Dict[str, Any]:
        """
        Aggregate results from multiple subtasks.
        
        Args:
            results: List of agent responses
            
        Returns:
            Aggregated result
        """
        aggregated = {
            "total_subtasks": len(results),
            "successful": sum(1 for r in results if r.status == "success"),
            "failed": sum(1 for r in results if r.status == "error"),
            "results": [r.result for r in results if r.status == "success"]
        }
        
        return aggregated
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task status information
        """
        async with self._lock:
            orchestrated_task = self.tasks.get(task_id)
            if not orchestrated_task:
                return None
            
            return {
                "task_id": task_id,
                "description": orchestrated_task.task.description,
                "status": orchestrated_task.status.value,
                "assigned_agent": orchestrated_task.assigned_agent,
                "priority": orchestrated_task.task.priority.value,
                "created_at": orchestrated_task.created_at.isoformat(),
                "started_at": orchestrated_task.started_at.isoformat() if orchestrated_task.started_at else None,
                "completed_at": orchestrated_task.completed_at.isoformat() if orchestrated_task.completed_at else None,
                "result": orchestrated_task.result,
                "error": orchestrated_task.error
            }
    
    async def get_all_tasks(self, status: Optional[TaskStatus] = None) -> List[Dict[str, Any]]:
        """
        Get all tasks, optionally filtered by status.
        
        Args:
            status: Filter by status
            
        Returns:
            List of task information
        """
        async with self._lock:
            tasks = []
            
            for task_id, orchestrated_task in self.tasks.items():
                if status is None or orchestrated_task.status == status:
                    tasks.append({
                        "task_id": task_id,
                        "description": orchestrated_task.task.description,
                        "status": orchestrated_task.status.value,
                        "priority": orchestrated_task.task.priority.value,
                        "created_at": orchestrated_task.created_at.isoformat()
                    })
            
            return tasks
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get orchestrator statistics.
        
        Returns:
            Dictionary containing statistics
        """
        async with self._lock:
            total_tasks = len(self.tasks)
            pending_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)
            in_progress_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS)
            completed_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
            failed_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
            
            # Aggregate agent metrics
            agent_metrics = {}
            for agent_id, agent in self.agents.items():
                agent_metrics[agent_id] = agent.get_metrics()
        
        return {
            "is_running": self.is_running,
            "total_tasks": total_tasks,
            "pending_tasks": pending_tasks,
            "in_progress_tasks": in_progress_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "queue_size": self.task_queue.qsize(),
            "registered_agents": len(self.agents),
            "active_workers": len(self.worker_tasks),
            "max_concurrent_agents": self.max_concurrent_agents,
            "agent_metrics": agent_metrics
        }