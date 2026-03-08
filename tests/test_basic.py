"""
Basic tests for OMNI-AI system
"""

import pytest
import asyncio
from datetime import datetime, timedelta

from src.agents.base_agent import BaseAgent, Task, AgentResponse, TaskPriority, AgentCapabilities, AgentStatus
from src.agents.veritas import VeritasAgent
from src.security.aegis import AegisGuardian, SecurityLevel, ThreatType
from src.memory.working_memory import WorkingMemory
from src.nexus.orchestrator import NexusOrchestrator


class TestVeritasAgent:
    """Test suite for VERITAS agent."""
    
    @pytest.fixture
    def veritas_agent(self):
        """Create VERITAS agent instance."""
        return VeritasAgent()
    
    def test_agent_initialization(self, veritas_agent):
        """Test agent initialization."""
        assert veritas_agent.agent_id == "veritas"
        assert veritas_agent.clearance_level == 2
        assert len(veritas_agent.capabilities.skills) > 0
    
    def test_validate_task(self, veritas_agent):
        """Test task validation."""
        # Valid task
        valid_task = Task(
            id="test_1",
            description="Verify a fact",
            parameters={"task_type": "verify_fact", "claim": "Test claim"}
        )
        assert asyncio.run(veritas_agent.validate_task(valid_task))
        
        # Invalid task
        invalid_task = Task(
            id="test_2",
            description="Invalid task",
            parameters={"task_type": "invalid_type"}
        )
        assert not asyncio.run(veritas_agent.validate_task(invalid_task))
    
    def test_verify_fact(self, veritas_agent):
        """Test fact verification."""
        task = Task(
            id="test_verify",
            description="Verify a fact",
            parameters={
                "task_type": "verify_fact",
                "claim": "The Earth orbits the Sun",
                "context": "Astronomy"
            }
        )
        
        response = asyncio.run(veritas_agent.execute_task(task))
        assert response.status in ["success", "error"]
        assert response.task_id == "test_verify"
        assert response.agent_id == "veritas"
        assert response.execution_time >= 0


class TestAegisGuardian:
    """Test suite for AEGIS Guardian."""
    
    @pytest.fixture
    def aegis(self):
        """Create AEGIS Guardian instance."""
        return AegisGuardian(security_level=SecurityLevel.LEVEL_1)
    
    def test_initialization(self, aegis):
        """Test AEGIS initialization."""
        assert aegis.security_level == SecurityLevel.LEVEL_1
        assert len(aegis.malicious_regex) > 0
        assert len(aegis.sensitive_regex) > 0
    
    def test_filter_input_safe(self, aegis):
        """Test filtering safe input."""
        safe_input = "This is a safe message."
        result = asyncio.run(aegis.filter_input(safe_input))
        
        assert result.is_safe
        assert result.filtered_content == safe_input
        assert len(result.threats) == 0
    
    def test_filter_input_malicious(self, aegis):
        """Test filtering malicious input."""
        malicious_input = "Test <script>alert('xss')</script> content"
        result = asyncio.run(aegis.filter_input(malicious_input))
        
        assert not result.is_safe
        assert "[REDACTED]" in result.filtered_content
        assert ThreatType.CODE_INJECTION in result.threats
    
    def test_get_security_events(self, aegis):
        """Test retrieving security events."""
        events = asyncio.run(aegis.get_security_events(limit=10))
        assert isinstance(events, list)
    
    def test_get_stats(self, aegis):
        """Test getting security statistics."""
        stats = asyncio.run(aegis.get_stats())
        assert "security_level" in stats
        assert "total_events" in stats
        assert "events_by_type" in stats


class TestWorkingMemory:
    """Test suite for Working Memory."""
    
    @pytest.fixture
    def working_memory(self):
        """Create Working Memory instance."""
        return WorkingMemory(max_size=10, default_ttl=60)
    
    def test_set_and_get(self, working_memory):
        """Test setting and getting values."""
        asyncio.run(working_memory.set("key1", "value1"))
        value = asyncio.run(working_memory.get("key1"))
        
        assert value == "value1"
    
    def test_get_nonexistent(self, working_memory):
        """Test getting non-existent key."""
        value = asyncio.run(working_memory.get("nonexistent"))
        assert value is None
    
    def test_delete(self, working_memory):
        """Test deleting values."""
        asyncio.run(working_memory.set("key1", "value1"))
        result = asyncio.run(working_memory.delete("key1"))
        
        assert result is True
        value = asyncio.run(working_memory.get("key1"))
        assert value is None
    
    def test_size_limit(self, working_memory):
        """Test size limit enforcement."""
        # Fill memory beyond limit
        for i in range(15):
            asyncio.run(working_memory.set(f"key{i}", f"value{i}"))
        
        size = asyncio.run(working_memory.get_size())
        assert size <= 10  # Max size
    
    def test_get_stats(self, working_memory):
        """Test getting memory statistics."""
        asyncio.run(working_memory.set("key1", "value1"))
        stats = asyncio.run(working_memory.get_stats())
        
        assert stats["size"] >= 1
        assert stats["max_size"] == 10
        assert "usage_percent" in stats


class TestNexusOrchestrator:
    """Test suite for NEXUS Orchestrator."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create NEXUS Orchestrator instance."""
        return NexusOrchestrator(max_concurrent_agents=2)
    
    def test_initialization(self, orchestrator):
        """Test orchestrator initialization."""
        assert orchestrator.max_concurrent_agents == 2
        assert len(orchestrator.agents) == 0
        assert not orchestrator.is_running
    
    def test_register_agent(self, orchestrator):
        """Test registering an agent."""
        agent = VeritasAgent()
        capabilities = AgentCapabilities(
            name="VERITAS",
            description="Test agent",
            skills=["test"],
            tools=["test"],
            max_concurrent_tasks=1
        )
        
        asyncio.run(orchestrator.register_agent(agent, capabilities))
        
        assert "veritas" in orchestrator.agents
    
    def test_submit_task(self, orchestrator):
        """Test submitting a task."""
        task_id = asyncio.run(orchestrator.submit_task(
            description="Test task",
            parameters={"test": "value"},
            priority=TaskPriority.MEDIUM
        ))
        
        assert task_id.startswith("task_")
        assert task_id in orchestrator.tasks
    
    def test_get_task_status(self, orchestrator):
        """Test getting task status."""
        task_id = asyncio.run(orchestrator.submit_task(
            description="Test task"
        ))
        
        status = asyncio.run(orchestrator.get_task_status(task_id))
        
        assert status is not None
        assert status["task_id"] == task_id
        assert "status" in status
    
    def test_get_stats(self, orchestrator):
        """Test getting orchestrator statistics."""
        stats = asyncio.run(orchestrator.get_stats())
        
        assert "is_running" in stats
        assert "total_tasks" in stats
        assert "registered_agents" in stats
        assert "max_concurrent_agents" in stats


class TestBaseAgentComponents:
    """Tests for BaseAgent components - Task, AgentResponse, etc."""
    
    def test_task_to_dict(self):
        """Test Task.to_dict() method."""
        task = Task(
            id="test-task-1",
            description="Test task description",
            parameters={"key": "value"},
            priority=TaskPriority.HIGH
        )
        
        result = task.to_dict()
        
        assert result["id"] == "test-task-1"
        assert result["description"] == "Test task description"
        assert result["parameters"] == {"key": "value"}
        assert result["priority"] == 2  # TaskPriority.HIGH.value
        assert "created_at" in result
    
    def test_task_to_dict_with_deadline(self):
        """Test Task.to_dict() with deadline."""
        task = Task(
            id="test-task-2",
            description="Task with deadline",
            parameters={},
            priority=TaskPriority.MEDIUM,
            deadline=datetime.utcnow() + timedelta(hours=1)
        )
        
        result = task.to_dict()
        
        assert result["deadline"] is not None
    
    def test_agent_response_to_dict(self):
        """Test AgentResponse.to_dict() method."""
        response = AgentResponse(
            task_id="task-1",
            agent_id="agent-1",
            status="success",
            result={"output": "done"},
            execution_time=1.5
        )
        
        result = response.to_dict()
        
        assert result["task_id"] == "task-1"
        assert result["agent_id"] == "agent-1"
        assert result["status"] == "success"
        assert result["result"] == {"output": "done"}
        assert result["execution_time"] == 1.5
    
    def test_agent_response_with_error(self):
        """Test AgentResponse with error."""
        response = AgentResponse(
            task_id="task-2",
            agent_id="agent-1",
            status="error",
            error="Something went wrong",
            execution_time=0.5
        )
        
        result = response.to_dict()
        
        assert result["status"] == "error"
        assert result["error"] == "Something went wrong"
    
    def test_agent_response_with_metadata(self):
        """Test AgentResponse with metadata."""
        response = AgentResponse(
            task_id="task-3",
            agent_id="agent-1",
            status="success",
            result={},
            metadata={"custom": "data"}
        )
        
        result = response.to_dict()
        
        assert result["metadata"] == {"custom": "data"}


class TestBaseAgentAsyncMethods:
    """Tests for BaseAgent async methods that need a concrete implementation."""
    
    @pytest.fixture
    def concrete_agent(self):
        """Create a concrete agent for testing."""
        from src.agents.base_agent import BaseAgent, AgentCapabilities
        from src.agents.base_agent import AgentStatus
        
        class ConcreteAgent(BaseAgent):
            """Concrete implementation of BaseAgent for testing."""
            
            async def execute_task(self, task):
                from src.agents.base_agent import AgentResponse
                return AgentResponse(
                    task_id=task.id,
                    agent_id=self.agent_id,
                    status="success",
                    result={"output": "done"}
                )
            
            async def validate_task(self, task):
                return True
        
        return ConcreteAgent(
            agent_id="test-agent",
            capabilities=AgentCapabilities(
                name="test",
                description="Test agent",
                skills=["test"],
                tools=[]
            ),
            clearance_level=1
        )
    
    @pytest.mark.asyncio
    async def test_initialize(self, concrete_agent):
        """Test agent initialization."""
        await concrete_agent.initialize()
        # Should complete without error
        assert True
    
    @pytest.mark.asyncio
    async def test_shutdown(self, concrete_agent):
        """Test agent shutdown."""
        await concrete_agent.shutdown()
        # Should complete without error
        assert True
    
    @pytest.mark.asyncio
    async def test_get_status(self, concrete_agent):
        """Test getting agent status."""
        status = await concrete_agent.get_status()
        assert status == AgentStatus.IDLE
    
    @pytest.mark.asyncio
    async def test_set_status(self, concrete_agent):
        """Test setting agent status."""
        await concrete_agent.set_status(AgentStatus.PROCESSING)
        status = await concrete_agent.get_status()
        assert status == AgentStatus.PROCESSING
    
    @pytest.mark.asyncio
    async def test_add_task(self, concrete_agent):
        """Test adding task to agent."""
        await concrete_agent.add_task("task-1")
        assert "task-1" in concrete_agent.current_tasks
    
    @pytest.mark.asyncio
    async def test_remove_task(self, concrete_agent):
        """Test removing task from agent."""
        await concrete_agent.add_task("task-1")
        await concrete_agent.remove_task("task-1")
        assert "task-1" not in concrete_agent.current_tasks
    
    @pytest.mark.asyncio
    async def test_remove_task_not_present(self, concrete_agent):
        """Test removing task that doesn't exist."""
        # Should not raise error
        await concrete_agent.remove_task("non-existent-task")
        assert True
    
    @pytest.mark.asyncio
    async def test_get_task_count(self, concrete_agent):
        """Test getting task count."""
        await concrete_agent.add_task("task-1")
        await concrete_agent.add_task("task-2")
        count = await concrete_agent.get_task_count()
        assert count == 2
    
    def test_record_response(self, concrete_agent):
        """Test recording response to history."""
        from src.agents.base_agent import AgentResponse
        
        response = AgentResponse(
            task_id="task-1",
            agent_id="test-agent",
            status="success",
            result={}
        )
        
        concrete_agent.record_response(response)
        assert len(concrete_agent.task_history) == 1
    
    def test_record_response_truncates_history(self, concrete_agent):
        """Test that recording responses truncates history to 1000 items."""
        from src.agents.base_agent import AgentResponse
        
        # Add 1001 responses
        for i in range(1001):
            response = AgentResponse(
                task_id=f"task-{i}",
                agent_id="test-agent",
                status="success",
                result={}
            )
            concrete_agent.record_response(response)
        
        # Should be truncated to 1000
        assert len(concrete_agent.task_history) == 1000
    
    def test_get_metrics_empty_history(self, concrete_agent):
        """Test getting metrics with empty history."""
        metrics = concrete_agent.get_metrics()
        
        assert metrics["agent_id"] == "test-agent"
        assert metrics["status"] == "idle"
        assert metrics["total_tasks_completed"] == 0
        assert metrics["success_rate"] == 0.0
        assert metrics["average_execution_time"] == 0.0
    
    def test_get_metrics_with_history(self, concrete_agent):
        """Test getting metrics with task history."""
        from src.agents.base_agent import AgentResponse
        
        # Add some responses
        for i in range(5):
            response = AgentResponse(
                task_id=f"task-{i}",
                agent_id="test-agent",
                status="success" if i < 3 else "error",
                result={},
                execution_time=1.0 + i * 0.5
            )
            concrete_agent.record_response(response)
        
        metrics = concrete_agent.get_metrics()
        
        assert metrics["total_tasks_completed"] == 5
        assert metrics["successful_tasks"] == 3
        assert metrics["failed_tasks"] == 2
        assert metrics["success_rate"] == 3 / 5
    
    def test_repr(self, concrete_agent):
        """Test agent string representation."""
        repr_str = repr(concrete_agent)
        assert "test-agent" in repr_str
        assert "idle" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])