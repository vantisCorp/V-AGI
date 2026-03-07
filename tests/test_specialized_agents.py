"""
Tests for Specialized Agents
Tests all 9 specialized agents in the OMNI-AI system
"""

import pytest
from unittest.mock import Mock, patch
from src.agents.base_agent import Task, TaskPriority

from src.agents.veritas import VeritasAgent
from src.agents.cerberus import CerberusAgent
from src.agents.muse import MuseAgent
from src.agents.forge import ForgeAgent
from src.agents.vita import VitaAgent
from src.agents.ares import AresAgent
from src.agents.lex_core import LEXCoreAgent
from src.agents.ludus import LUDUSAgent
from src.agents.argus import ARGUSAgent


class TestVeritasAgent:
    """Test suite for VERITAS Agent (Truth Verification)."""
    
    @pytest.fixture
    def agent(self):
        """Create VERITAS agent instance."""
        return VeritasAgent()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert agent.agent_id == "veritas"
    
    @pytest.mark.asyncio
    async def test_validate_task(self, agent):
        """Test task validation."""
        task = Task(
            id="test_task",
            description="Verify a fact",
            parameters={"claim": "The Earth is round"},
            priority=TaskPriority.MEDIUM
        )
        result = await agent.validate_task(task)
        assert isinstance(result, bool)
    
    @pytest.mark.asyncio
    async def test_execute_task(self, agent):
        """Test fact verification task."""
        task = Task(
            id="test_task",
            description="Verify a fact",
            parameters={"claim": "The Earth is round", "task_type": "verify_fact"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'status')


class TestCerberusAgent:
    """Test suite for CERBERUS Agent (Security)."""
    
    @pytest.fixture
    def agent(self):
        """Create CERBERUS agent instance."""
        return CerberusAgent()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert agent.agent_id == "cerberus"
    
    @pytest.mark.asyncio
    async def test_validate_task(self, agent):
        """Test task validation."""
        task = Task(
            id="test_task",
            description="Monitor security",
            parameters={"action": "scan"},
            priority=TaskPriority.HIGH
        )
        result = await agent.validate_task(task)
        assert isinstance(result, bool)
    
    @pytest.mark.asyncio
    async def test_execute_task(self, agent):
        """Test security task execution."""
        task = Task(
            id="test_task",
            description="Monitor security",
            parameters={"action": "scan", "task_type": "monitor_threats"},
            priority=TaskPriority.HIGH
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'status')


class TestMuseAgent:
    """Test suite for MUSE Agent (Creative)."""
    
    @pytest.fixture
    def agent(self):
        """Create MUSE agent instance."""
        return MuseAgent()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert agent.agent_id == "muse"
    
    @pytest.mark.asyncio
    async def test_execute_task(self, agent):
        """Test creative task execution."""
        task = Task(
            id="test_task",
            description="Generate content",
            parameters={"content_type": "story", "topic": "AI", "task_type": "generate_content"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'status')


class TestForgeAgent:
    """Test suite for FORGE Agent (Design & Engineering)."""
    
    @pytest.fixture
    def agent(self):
        """Create FORGE agent instance."""
        return ForgeAgent()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert agent.agent_id == "forge"
    
    @pytest.mark.asyncio
    async def test_execute_task(self, agent):
        """Test design task execution."""
        task = Task(
            id="test_task",
            description="Design a component",
            parameters={"component_type": "bracket", "requirements": {}, "task_type": "design_component"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'status')


class TestVitaAgent:
    """Test suite for VITA Agent (Healthcare)."""
    
    @pytest.fixture
    def agent(self):
        """Create VITA agent instance."""
        return VitaAgent()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert agent.agent_id == "vita"
    
    @pytest.mark.asyncio
    async def test_execute_task(self, agent):
        """Test healthcare task execution."""
        task = Task(
            id="test_task",
            description="Analyze symptoms",
            parameters={"symptoms": ["fever", "cough"], "task_type": "analyze_symptoms"},
            priority=TaskPriority.HIGH
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'status')


class TestAresAgent:
    """Test suite for ARES Agent (Strategic Planning)."""
    
    @pytest.fixture
    def agent(self):
        """Create ARES agent instance."""
        return AresAgent()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert agent.agent_id == "ares"
    
    @pytest.mark.asyncio
    async def test_execute_task(self, agent):
        """Test strategic planning task execution."""
        task = Task(
            id="test_task",
            description="Create strategic plan",
            parameters={"objectives": ["Increase efficiency"], "task_type": "create_strategic_plan"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'status')


class TestLEXCoreAgent:
    """Test suite for LEX-Core Agent (Legal & Compliance)."""
    
    @pytest.fixture
    def agent(self):
        """Create LEX-Core agent instance."""
        return LEXCoreAgent()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert agent.agent_id == "lex_core"
    
    @pytest.mark.asyncio
    async def test_execute_task(self, agent):
        """Test legal analysis task execution."""
        task = Task(
            id="test_task",
            description="Analyze legal document",
            parameters={"document_type": "contract", "content": "sample text", "task_type": "legal_document_analysis"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'status')


class TestLUDUSAgent:
    """Test suite for LUDUS Agent (Simulation & Gaming)."""
    
    @pytest.fixture
    def agent(self):
        """Create LUDUS agent instance."""
        return LUDUSAgent()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert agent.agent_id == "ludus"
    
    @pytest.mark.asyncio
    async def test_execute_task(self, agent):
        """Test simulation task execution."""
        task = Task(
            id="test_task",
            description="Run simulation",
            parameters={"simulation_type": "physics", "scenario": "projectile", "task_type": "physics_simulation"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'status')


class TestARGUSAgent:
    """Test suite for ARGUS Agent (Monitoring & Analytics)."""
    
    @pytest.fixture
    def agent(self):
        """Create ARGUS agent instance."""
        return ARGUSAgent()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert agent.agent_id == "argus"
        assert hasattr(agent, 'metrics_database')
        assert hasattr(agent, 'task_history')
    
    @pytest.mark.asyncio
    async def test_execute_real_time_monitoring(self, agent):
        """Test real-time monitoring task."""
        task = Task(
            id="test_monitor_1",
            description="Monitor system",
            parameters={"scope": "system", "metrics": ["cpu_usage", "memory_usage"], "task_type": "real_time_monitoring"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert response.agent_id == "argus"
        assert response.task_id == "test_monitor_1"
    
    @pytest.mark.asyncio
    async def test_execute_performance_analytics(self, agent):
        """Test performance analytics task."""
        task = Task(
            id="test_perf_1",
            description="Analyze performance",
            parameters={"task_type": "performance_analytics", "time_range": "1h"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_log_analysis(self, agent):
        """Test log analysis task."""
        task = Task(
            id="test_log_1",
            description="Analyze logs",
            parameters={"task_type": "log_analysis", "log_source": "application"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_alert_management(self, agent):
        """Test alert management task."""
        task = Task(
            id="test_alert_1",
            description="Manage alerts",
            parameters={"task_type": "alert_management", "action": "list"},
            priority=TaskPriority.HIGH
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_trend_analysis(self, agent):
        """Test trend analysis task."""
        task = Task(
            id="test_trend_1",
            description="Analyze trends",
            parameters={"task_type": "trend_analysis", "metric": "cpu_usage"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_anomaly_detection(self, agent):
        """Test anomaly detection task."""
        task = Task(
            id="test_anomaly_1",
            description="Detect anomalies",
            parameters={"task_type": "anomaly_detection", "sensitivity": "high"},
            priority=TaskPriority.HIGH
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_dashboard_generation(self, agent):
        """Test dashboard generation task."""
        task = Task(
            id="test_dashboard_1",
            description="Generate dashboard",
            parameters={"task_type": "dashboard_generation", "dashboard_type": "system"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_report_generation(self, agent):
        """Test report generation task."""
        task = Task(
            id="test_report_1",
            description="Generate report",
            parameters={"task_type": "report_generation", "report_type": "daily"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_unknown_task_type(self, agent):
        """Test handling of unknown task type."""
        from src.agents.base_agent import AgentStatus
        task = Task(
            id="test_unknown_1",
            description="Unknown task",
            parameters={"task_type": "unknown_type"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert response.status == AgentStatus.ERROR
    
    @pytest.mark.asyncio
    async def test_validate_task_success(self, agent):
        """Test task validation with valid result."""
        task = Task(
            id="test_validate_1",
            description="Test validation",
            parameters={"task_type": "real_time_monitoring"},
            priority=TaskPriority.MEDIUM
        )
        result = {"status": "success", "monitoring_results": {}}
        is_valid = await agent.validate_task(task, result)
        assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_metrics_tracking(self, agent):
        """Test that metrics are tracked correctly."""
        initial_received = agent.metrics.tasks_received
        initial_completed = agent.metrics.tasks_completed
        
        task = Task(
            id="test_metrics_1",
            description="Test metrics",
            parameters={"task_type": "real_time_monitoring"},
            priority=TaskPriority.MEDIUM
        )
        await agent.execute_task(task)
        
        assert agent.metrics.tasks_received == initial_received + 1
        assert agent.metrics.tasks_completed == initial_completed + 1
    
    @pytest.mark.asyncio
    async def test_task_history_tracking(self, agent):
        """Test that failed tasks are recorded in history."""
        task = Task(
            id="test_history_1",
            description="Test history",
            parameters={"task_type": "unknown_type"},
            priority=TaskPriority.MEDIUM
        )
        await agent.execute_task(task)
        
        # Task should be recorded in history due to error
        assert "test_history_1" in agent.task_history


if __name__ == "__main__":
    pytest.main([__file__, "-v"])