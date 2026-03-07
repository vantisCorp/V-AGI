"""
Base Agent Class for OMNI-AI
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio


class AgentStatus(Enum):
    """Agent status enumeration."""
    IDLE = "idle"
    PROCESSING = "processing"
    WAITING = "waiting"
    ERROR = "error"
    TERMINATED = "terminated"


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class Task:
    """Task data structure."""
    id: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: datetime = field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "parameters": self.parameters,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "dependencies": self.dependencies
        }


@dataclass
class AgentResponse:
    """Agent response data structure."""
    task_id: str
    agent_id: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "execution_time": self.execution_time,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class AgentCapabilities:
    """Agent capabilities definition."""
    name: str
    description: str
    skills: List[str]
    tools: List[str]
    max_concurrent_tasks: int = 1
    specialization: str = "general"


class BaseAgent(ABC):
    """
    Abstract base class for all OMNI-AI agents.
    
    All specialized agents must inherit from this class and implement
    the execute_task method.
    """
    
    def __init__(
        self,
        agent_id: str,
        capabilities: AgentCapabilities,
        clearance_level: int = 1
    ):
        """
        Initialize base agent.
        
        Args:
            agent_id: Unique identifier for the agent
            capabilities: Agent capabilities definition
            clearance_level: Security clearance level (1-3)
        """
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.clearance_level = clearance_level
        self.status = AgentStatus.IDLE
        self.current_tasks: List[str] = []
        self.task_history: List[AgentResponse] = []
        self._lock = asyncio.Lock()
        
    @abstractmethod
    async def execute_task(self, task: Task) -> AgentResponse:
        """
        Execute a task assigned to this agent.
        
        Args:
            task: Task to execute
            
        Returns:
            AgentResponse containing the result or error
        """
        pass
    
    @abstractmethod
    async def validate_task(self, task: Task) -> bool:
        """
        Validate if this agent can handle the given task.
        
        Args:
            task: Task to validate
            
        Returns:
            True if agent can handle the task, False otherwise
        """
        pass
    
    async def initialize(self) -> None:
        """Initialize agent resources."""
        pass
    
    async def shutdown(self) -> None:
        """Cleanup agent resources."""
        pass
    
    async def get_status(self) -> AgentStatus:
        """Get current agent status."""
        async with self._lock:
            return self.status
    
    async def set_status(self, status: AgentStatus) -> None:
        """Set agent status."""
        async with self._lock:
            self.status = status
    
    async def add_task(self, task_id: str) -> None:
        """Add task to current tasks list."""
        async with self._lock:
            self.current_tasks.append(task_id)
    
    async def remove_task(self, task_id: str) -> None:
        """Remove task from current tasks list."""
        async with self._lock:
            if task_id in self.current_tasks:
                self.current_tasks.remove(task_id)
    
    async def get_task_count(self) -> int:
        """Get number of currently running tasks."""
        async with self._lock:
            return len(self.current_tasks)
    
    def record_response(self, response: AgentResponse) -> None:
        """Record agent response to history."""
        self.task_history.append(response)
        
        # Keep only last 1000 responses
        if len(self.task_history) > 1000:
            self.task_history = self.task_history[-1000:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get agent metrics.
        
        Returns:
            Dictionary containing agent metrics
        """
        successful_tasks = sum(1 for r in self.task_history if r.status == "success")
        failed_tasks = sum(1 for r in self.task_history if r.status == "error")
        
        total_execution_time = sum(r.execution_time for r in self.task_history)
        avg_execution_time = total_execution_time / len(self.task_history) if self.task_history else 0.0
        
        return {
            "agent_id": self.agent_id,
            "status": self.status.value,
            "current_tasks": len(self.current_tasks),
            "total_tasks_completed": len(self.task_history),
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": successful_tasks / len(self.task_history) if self.task_history else 0.0,
            "average_execution_time": avg_execution_time,
            "clearance_level": self.clearance_level,
            "capabilities": self.capabilities.name
        }
    
    def __repr__(self) -> str:
        return f"BaseAgent(id={self.agent_id}, status={self.status.value}, tasks={len(self.current_tasks)})"