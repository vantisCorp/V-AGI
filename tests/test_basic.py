"""
Basic tests for OMNI-AI system
"""

import pytest
import asyncio
from datetime import datetime, timedelta

from src.agents.base_agent import BaseAgent, Task, AgentResponse, TaskPriority, AgentCapabilities
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])