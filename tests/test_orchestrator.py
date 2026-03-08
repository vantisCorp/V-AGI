"""
Tests for NEXUS Orchestrator.
"""

import asyncio

# Import Task and TaskPriority from the same module the orchestrator uses
import sys
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from src.nexus.orchestrator import AgentAssignment, NexusOrchestrator, OrchestratedTask, TaskStatus

sys.path.insert(0, "src")
from agents.base_agent import AgentCapabilities, AgentResponse, BaseAgent, Task, TaskPriority


class TestOrchestratedTask:
    """Test suite for OrchestratedTask dataclass."""

    def test_orchestrated_task_creation(self):
        """Test creating an orchestrated task."""
        task = Task(id="test-1", description="Test task")
        orchestrated = OrchestratedTask(task=task, status=TaskStatus.PENDING)
        assert orchestrated.task.id == "test-1"
        assert orchestrated.status == TaskStatus.PENDING


class TestAgentAssignment:
    """Test suite for AgentAssignment dataclass."""

    def test_agent_assignment_creation(self):
        """Test creating an agent assignment."""
        assignment = AgentAssignment(agent_id="agent-1", task_id="task-1")
        assert assignment.agent_id == "agent-1"
        assert assignment.task_id == "task-1"
        assert assignment.assigned_at is not None
        assert assignment.priority.value == TaskPriority.MEDIUM.value


class TestNexusOrchestrator:
    """Test suite for NEXUS Orchestrator."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return NexusOrchestrator(max_concurrent_agents=5)

    @pytest.fixture
    def mock_agent(self):
        """Create mock agent."""
        agent = AsyncMock(spec=BaseAgent)
        agent.agent_id = "test-agent"
        agent.execute_task = AsyncMock(
            return_value=AgentResponse(
                agent_id="test-agent", task_id="test-task", status="idle", result={"success": True}
            )
        )
        return agent

    @pytest.fixture
    def mock_capabilities(self):
        """Create mock capabilities."""
        return AgentCapabilities(
            name="test-agent",
            description="Test agent",
            skills=["analysis", "processing"],
            tools=["tool1", "tool2"],
        )

    def test_init(self, orchestrator):
        """Test initialization."""
        assert orchestrator.max_concurrent_agents == 5
        assert len(orchestrator.agents) == 0
        assert len(orchestrator.tasks) == 0
        assert orchestrator.is_running is False

    @pytest.mark.asyncio
    async def test_register_agent(self, orchestrator, mock_agent, mock_capabilities):
        """Test registering an agent."""
        await orchestrator.register_agent(mock_agent, mock_capabilities)

        assert "test-agent" in orchestrator.agents
        assert "test-agent" in orchestrator.agent_capabilities

    @pytest.mark.asyncio
    async def test_unregister_agent(self, orchestrator, mock_agent, mock_capabilities):
        """Test unregistering an agent."""
        await orchestrator.register_agent(mock_agent, mock_capabilities)
        await orchestrator.unregister_agent("test-agent")

        assert "test-agent" not in orchestrator.agents

    @pytest.mark.asyncio
    async def test_unregister_nonexistent_agent(self, orchestrator):
        """Test unregistering a non-existent agent."""
        # Should not raise
        await orchestrator.unregister_agent("nonexistent-agent")

    @pytest.mark.asyncio
    async def test_submit_task(self, orchestrator, mock_agent, mock_capabilities):
        """Test submitting a task."""
        await orchestrator.register_agent(mock_agent, mock_capabilities)

        task = Task(id="test-task-1", description="Test task", priority=TaskPriority.MEDIUM)

        task_id = await orchestrator.submit_task(task)
        assert task_id is not None

    @pytest.mark.asyncio
    async def test_get_task_status(self, orchestrator, mock_agent, mock_capabilities):
        """Test getting task status."""
        await orchestrator.register_agent(mock_agent, mock_capabilities)

        task = Task(id="test-task-2", description="Test task", priority=TaskPriority.MEDIUM)

        task_id = await orchestrator.submit_task(task)
        status = await orchestrator.get_task_status(task_id)

        assert status is not None
        assert "task_id" in status

    @pytest.mark.asyncio
    async def test_get_task_status_nonexistent(self, orchestrator):
        """Test getting status for non-existent task."""
        status = await orchestrator.get_task_status("nonexistent-task")
        assert status is None

    @pytest.mark.asyncio
    async def test_get_all_tasks(self, orchestrator, mock_agent, mock_capabilities):
        """Test getting all tasks."""
        await orchestrator.register_agent(mock_agent, mock_capabilities)

        task1 = Task(id="task-1", description="Task 1", priority=TaskPriority.LOW)
        task2 = Task(id="task-2", description="Task 2", priority=TaskPriority.HIGH)

        await orchestrator.submit_task(task1)
        await orchestrator.submit_task(task2)

        all_tasks = await orchestrator.get_all_tasks()
        assert len(all_tasks) >= 2

    @pytest.mark.asyncio
    async def test_get_stats(self, orchestrator):
        """Test getting orchestrator stats."""
        stats = await orchestrator.get_stats()

        assert stats is not None
        assert "is_running" in stats
        assert "registered_agents" in stats

    @pytest.mark.asyncio
    async def test_start_and_stop(self, orchestrator):
        """Test starting and stopping orchestrator."""
        await orchestrator.start()
        assert orchestrator.is_running is True

        await orchestrator.stop()
        assert orchestrator.is_running is False

    @pytest.mark.asyncio
    async def test_stop_when_not_running(self, orchestrator):
        """Test stopping when not running."""
        # Should not raise
        await orchestrator.stop()

    @pytest.mark.asyncio
    async def test_select_agent(self, orchestrator, mock_agent, mock_capabilities):
        """Test agent selection."""
        # Add capabilities to the mock agent
        mock_agent.capabilities = mock_capabilities
        mock_agent.get_status = AsyncMock(return_value=MagicMock(value="idle"))
        mock_agent.get_task_count = AsyncMock(return_value=0)

        await orchestrator.register_agent(mock_agent, mock_capabilities)

        task = Task(
            id="test-task-3",
            description="Test task",
            parameters={"task_type": "analysis"},
            priority=TaskPriority.MEDIUM,
        )

        selected = await orchestrator._select_agent(task)
        # Should select the agent since it's idle
        assert selected is not None
        assert selected.agent_id == "test-agent"


class TestOrchestratorIntegration:
    """Integration tests for orchestrator."""

    @pytest.mark.asyncio
    async def test_full_task_lifecycle(self):
        """Test full task lifecycle."""
        orchestrator = NexusOrchestrator(max_concurrent_agents=2)

        # Create and register mock agent
        mock_agent = AsyncMock(spec=BaseAgent)
        mock_agent.agent_id = "worker-1"
        mock_agent.execute_task = AsyncMock(
            return_value=AgentResponse(
                agent_id="worker-1",
                task_id="lifecycle-task",
                status="idle",
                result={"processed": True},
            )
        )

        capabilities = AgentCapabilities(
            name="worker-1", description="Worker agent", skills=["processing"], tools=[]
        )

        await orchestrator.register_agent(mock_agent, capabilities)

        # Submit task
        task = Task(
            id="lifecycle-task", description="Lifecycle test task", priority=TaskPriority.HIGH
        )

        task_id = await orchestrator.submit_task(task)
        # Task ID is generated by the orchestrator with format task_{uuid}
        assert task_id.startswith("task_")

        # Check task exists
        status = await orchestrator.get_task_status(task_id)
        assert status is not None

    @pytest.mark.asyncio
    async def test_multiple_agents(self):
        """Test with multiple agents."""
        orchestrator = NexusOrchestrator(max_concurrent_agents=5)

        # Register multiple agents
        for i in range(3):
            agent = AsyncMock(spec=BaseAgent)
            agent.agent_id = f"agent-{i}"
            capabilities = AgentCapabilities(
                name=f"agent-{i}", description=f"Agent {i}", skills=["task"], tools=[]
            )
            await orchestrator.register_agent(agent, capabilities)

        stats = await orchestrator.get_stats()
        assert stats["registered_agents"] == 3


class TestOrchestratorWorkerProcessing:
    """Tests for worker task processing."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return NexusOrchestrator(max_concurrent_agents=2)

    @pytest.fixture
    def mock_agent(self):
        """Create mock agent."""
        agent = AsyncMock(spec=BaseAgent)
        agent.agent_id = "test-agent"
        agent.capabilities = MagicMock(max_concurrent_tasks=5)
        agent.get_status = AsyncMock(return_value=MagicMock(value="idle"))
        agent.get_task_count = AsyncMock(return_value=0)
        agent.execute_task = AsyncMock(
            return_value=AgentResponse(
                agent_id="test-agent",
                task_id="test-task",
                status="success",
                result={"success": True},
            )
        )
        agent.record_response = Mock()
        return agent

    @pytest.fixture
    def mock_capabilities(self):
        """Create mock capabilities."""
        return AgentCapabilities(
            name="test-agent",
            description="Test agent",
            skills=["analysis", "processing"],
            tools=["tool1"],
        )

    @pytest.mark.asyncio
    async def test_worker_processes_task(self, orchestrator, mock_agent, mock_capabilities):
        """Test that worker processes tasks from queue."""
        await orchestrator.register_agent(mock_agent, mock_capabilities)

        # Submit a task
        task_id = await orchestrator.submit_task(
            description="Test task", parameters={"key": "value"}, priority=TaskPriority.MEDIUM
        )

        # Start orchestrator briefly to process
        await orchestrator.start()
        await asyncio.sleep(0.2)  # Give worker time to process
        await orchestrator.stop()

        # Check task was processed
        status = await orchestrator.get_task_status(task_id)
        assert status is not None

    @pytest.mark.asyncio
    async def test_worker_timeout(self, orchestrator):
        """Test worker handles timeout when queue is empty."""
        await orchestrator.start()
        await asyncio.sleep(0.1)  # Let worker timeout once
        await orchestrator.stop()
        # Should complete without error
        assert True

    @pytest.mark.asyncio
    async def test_process_task_not_found(self, orchestrator):
        """Test processing when task not found."""
        # Try to process non-existent task
        await orchestrator._process_task("nonexistent-task", "worker-0")
        # Should not raise error
        assert True

    @pytest.mark.asyncio
    async def test_execute_subtask_no_agent(self, orchestrator):
        """Test executing subtask when no agent available."""
        task = Task(
            id="subtask-1", description="Subtask", parameters={}, priority=TaskPriority.MEDIUM
        )

        response = await orchestrator._execute_subtask(task, "worker-0")

        assert response.agent_id == "none"
        assert response.status == "error"
        assert "No suitable agent found" in response.error

    @pytest.mark.asyncio
    async def test_execute_task_direct_no_agent(self, orchestrator):
        """Test executing task directly when no agent available."""
        task = Task(
            id="direct-task", description="Direct task", parameters={}, priority=TaskPriority.MEDIUM
        )

        response = await orchestrator._execute_task_direct(task, "worker-0")

        assert response.agent_id == "none"
        assert response.status == "error"

    @pytest.mark.asyncio
    async def test_execute_subtask_with_agent(self, orchestrator, mock_agent, mock_capabilities):
        """Test executing subtask with available agent."""
        await orchestrator.register_agent(mock_agent, mock_capabilities)

        task = Task(
            id="subtask-2", description="Subtask", parameters={}, priority=TaskPriority.MEDIUM
        )

        response = await orchestrator._execute_subtask(task, "worker-0")

        assert response.agent_id == "test-agent"
        assert response.status == "success"
        mock_agent.record_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_task_direct_with_agent(
        self, orchestrator, mock_agent, mock_capabilities
    ):
        """Test executing task directly with available agent."""
        await orchestrator.register_agent(mock_agent, mock_capabilities)

        task = Task(
            id="direct-task-2",
            description="Direct task",
            parameters={},
            priority=TaskPriority.MEDIUM,
        )

        response = await orchestrator._execute_task_direct(task, "worker-0")

        assert response.agent_id == "test-agent"
        assert response.status == "success"


class TestTaskDecomposition:
    """Tests for task decomposition."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return NexusOrchestrator(max_concurrent_agents=2)

    @pytest.mark.asyncio
    async def test_decompose_critical_task(self, orchestrator):
        """Test decomposition of critical priority task."""
        task = Task(
            id="critical-task",
            description="Critical operation",
            parameters={"key": "value"},
            priority=TaskPriority.CRITICAL,
        )

        subtasks = await orchestrator._decompose_task(task)

        assert len(subtasks) == 3
        for i, subtask in enumerate(subtasks):
            assert f"Subtask {i+1}" in subtask.description
            assert subtask.priority == TaskPriority.HIGH

    @pytest.mark.asyncio
    async def test_decompose_non_critical_task(self, orchestrator):
        """Test that non-critical tasks are not decomposed."""
        for priority in [TaskPriority.LOW, TaskPriority.MEDIUM, TaskPriority.HIGH]:
            task = Task(
                id=f"task-{priority.value}",
                description="Regular task",
                parameters={},
                priority=priority,
            )

            subtasks = await orchestrator._decompose_task(task)
            assert len(subtasks) == 0


class TestResultAggregation:
    """Tests for result aggregation."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return NexusOrchestrator(max_concurrent_agents=2)

    @pytest.mark.asyncio
    async def test_aggregate_results_all_success(self, orchestrator):
        """Test aggregating all successful results."""
        results = [
            AgentResponse(agent_id="a1", task_id="t1", status="success", result={"data": 1}),
            AgentResponse(agent_id="a2", task_id="t2", status="success", result={"data": 2}),
            AgentResponse(agent_id="a3", task_id="t3", status="success", result={"data": 3}),
        ]

        aggregated = await orchestrator._aggregate_results(results)

        assert aggregated["total_subtasks"] == 3
        assert aggregated["successful"] == 3
        assert aggregated["failed"] == 0
        assert len(aggregated["results"]) == 3

    @pytest.mark.asyncio
    async def test_aggregate_results_mixed(self, orchestrator):
        """Test aggregating mixed success/error results."""
        results = [
            AgentResponse(agent_id="a1", task_id="t1", status="success", result={"data": 1}),
            AgentResponse(agent_id="a2", task_id="t2", status="error", error="Failed", result=None),
            AgentResponse(agent_id="a3", task_id="t3", status="success", result={"data": 3}),
        ]

        aggregated = await orchestrator._aggregate_results(results)

        assert aggregated["total_subtasks"] == 3
        assert aggregated["successful"] == 2
        assert aggregated["failed"] == 1
        assert len(aggregated["results"]) == 2

    @pytest.mark.asyncio
    async def test_aggregate_results_all_failed(self, orchestrator):
        """Test aggregating all failed results."""
        results = [
            AgentResponse(agent_id="a1", task_id="t1", status="error", error="Error 1"),
            AgentResponse(agent_id="a2", task_id="t2", status="error", error="Error 2"),
        ]

        aggregated = await orchestrator._aggregate_results(results)

        assert aggregated["successful"] == 0
        assert aggregated["failed"] == 2
        assert len(aggregated["results"]) == 0


class TestAgentSelection:
    """Tests for agent selection logic."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return NexusOrchestrator(max_concurrent_agents=5)

    @pytest.mark.asyncio
    async def test_select_agent_least_tasks(self, orchestrator):
        """Test that agent with least tasks is selected."""
        # Register multiple agents with different task counts
        agents = []
        for i in range(3):
            agent = AsyncMock(spec=BaseAgent)
            agent.agent_id = f"agent-{i}"
            agent.capabilities = MagicMock(max_concurrent_tasks=5)
            agent.get_status = AsyncMock(return_value=MagicMock(value="idle"))
            agent.get_task_count = AsyncMock(return_value=i * 2)  # 0, 2, 4 tasks

            capabilities = AgentCapabilities(
                name=f"agent-{i}", description=f"Agent {i}", skills=["task"], tools=[]
            )
            await orchestrator.register_agent(agent, capabilities)
            agents.append(agent)

        task = Task(id="test-task", description="Test", parameters={}, priority=TaskPriority.MEDIUM)

        selected = await orchestrator._select_agent(task)

        # Should select agent-0 (0 tasks)
        assert selected.agent_id == "agent-0"

    @pytest.mark.asyncio
    async def test_select_agent_all_busy(self, orchestrator):
        """Test selection when all agents are at capacity."""
        for i in range(2):
            agent = AsyncMock(spec=BaseAgent)
            agent.agent_id = f"agent-{i}"
            agent.capabilities = MagicMock(max_concurrent_tasks=2)
            agent.get_status = AsyncMock(return_value=MagicMock(value="busy"))
            agent.get_task_count = AsyncMock(return_value=5)  # Over capacity

            capabilities = AgentCapabilities(
                name=f"agent-{i}", description=f"Agent {i}", skills=["task"], tools=[]
            )
            await orchestrator.register_agent(agent, capabilities)

        task = Task(id="test-task", description="Test", parameters={}, priority=TaskPriority.MEDIUM)

        selected = await orchestrator._select_agent(task)

        # Should return None when all agents busy
        assert selected is None


class TestTaskFiltering:
    """Tests for task filtering by status."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return NexusOrchestrator(max_concurrent_agents=2)

    @pytest.mark.asyncio
    async def test_get_all_tasks_filtered_by_status(self, orchestrator):
        """Test filtering tasks by status."""
        # Create tasks with different statuses
        task1 = OrchestratedTask(
            task=Task(id="t1", description="Task 1", parameters={}, priority=TaskPriority.LOW),
            status=TaskStatus.PENDING,
        )
        task2 = OrchestratedTask(
            task=Task(id="t2", description="Task 2", parameters={}, priority=TaskPriority.MEDIUM),
            status=TaskStatus.COMPLETED,
        )
        task3 = OrchestratedTask(
            task=Task(id="t3", description="Task 3", parameters={}, priority=TaskPriority.HIGH),
            status=TaskStatus.PENDING,
        )

        orchestrator.tasks = {"t1": task1, "t2": task2, "t3": task3}

        # Filter by PENDING
        pending = await orchestrator.get_all_tasks(status=TaskStatus.PENDING)
        assert len(pending) == 2

        # Filter by COMPLETED
        completed = await orchestrator.get_all_tasks(status=TaskStatus.COMPLETED)
        assert len(completed) == 1


class TestOrchestratorStartStop:
    """Tests for orchestrator start/stop behavior."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return NexusOrchestrator(max_concurrent_agents=2)

    @pytest.mark.asyncio
    async def test_start_already_running(self, orchestrator):
        """Test starting when already running."""
        await orchestrator.start()
        assert orchestrator.is_running is True

        # Start again - should log warning but not error
        await orchestrator.start()
        assert orchestrator.is_running is True

        await orchestrator.stop()

    @pytest.mark.asyncio
    async def test_stop_cancels_workers(self, orchestrator):
        """Test that stop cancels all worker tasks."""
        await orchestrator.start()
        assert len(orchestrator.worker_tasks) == 2

        await orchestrator.stop()
        assert len(orchestrator.worker_tasks) == 0
        assert orchestrator.is_running is False

    @pytest.mark.asyncio
    async def test_stop_shuts_down_agents(self, orchestrator):
        """Test that stop shuts down all agents."""
        # Register mock agents
        for i in range(2):
            agent = AsyncMock(spec=BaseAgent)
            agent.agent_id = f"agent-{i}"
            agent.shutdown = AsyncMock()
            capabilities = AgentCapabilities(
                name=f"agent-{i}", description=f"Agent {i}", skills=["task"], tools=[]
            )
            await orchestrator.register_agent(agent, capabilities)

        await orchestrator.start()
        await orchestrator.stop()

        # All agents should be shut down
        for agent in orchestrator.agents.values():
            agent.shutdown.assert_called()


class TestSubmitTaskVariations:
    """Tests for different task submission scenarios."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return NexusOrchestrator(max_concurrent_agents=2)

    @pytest.mark.asyncio
    async def test_submit_task_with_deadline(self, orchestrator):
        """Test submitting task with deadline."""
        deadline = datetime.utcnow()

        task_id = await orchestrator.submit_task(
            description="Task with deadline",
            parameters={"key": "value"},
            priority=TaskPriority.HIGH,
            deadline=deadline,
        )

        assert task_id.startswith("task_")
        status = await orchestrator.get_task_status(task_id)
        assert status is not None

    @pytest.mark.asyncio
    async def test_submit_task_no_parameters(self, orchestrator):
        """Test submitting task without parameters."""
        task_id = await orchestrator.submit_task(description="Simple task")

        assert task_id.startswith("task_")
        status = await orchestrator.get_task_status(task_id)
        assert status["description"] == "Simple task"
